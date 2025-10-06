// Vercel Edge Function to proxy UIUC Chat API
export const config = { runtime: 'edge' };

export default async function handler(req: Request) {
  // Handle CORS preflight if any environment triggers it
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Accept',
        'Access-Control-Max-Age': '86400'
      }
    });
  }

  if (req.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
  }

  try {
    const body = await req.json();

    const endpoints = [
      'https://uiuc.chat/api/chat-api/chat',
      'https://uiuc.chat/api/chat-api/chat/',
      // Fallback without the leading /api in case of server routing differences
      'https://uiuc.chat/chat-api/chat',
      'https://uiuc.chat/chat-api/chat/',
    ];

    let lastErrorText = '';
    let lastStatus = 500;
    for (const url of endpoints) {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      };

      // Some deployments require API key as header rather than body; include if present
      try {
        const maybeKey = (body as any)?.api_key as string | undefined;
        const maybeCourse = (body as any)?.course_name as string | undefined;
        if (maybeKey) {
          headers['Authorization'] = `Bearer ${maybeKey}`;
          headers['x-api-key'] = maybeKey;
        }
        if (maybeCourse) {
          headers['x-course-name'] = maybeCourse;
        }
      } catch {}

      const upstream = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
      });

      if (upstream.ok) {
        const contentType = upstream.headers.get('content-type') || 'text/event-stream';
        return new Response(upstream.body, {
          status: upstream.status,
          headers: {
            'Content-Type': contentType,
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*',
          },
        });
      }

      lastStatus = upstream.status;
      lastErrorText = (await upstream.text()) || upstream.statusText;

      // If Method Not Allowed, try next endpoint immediately
      if (upstream.status === 405) {
        continue;
      } else {
        break;
      }
    }

    // If none succeeded, surface the last error with extra context
    return new Response(`UIUC Chat upstream error (${lastStatus}): ${lastErrorText}`, { status: lastStatus });
  } catch (err) {
    // Surface a clearer error message
    const message = err instanceof Error ? err.message : 'Internal server error';
    return new Response(message, { status: 500 });
  }
}
