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

    // If POST attempts failed, try GET with query params (some SSE endpoints are GET-only)
    try {
      const params = new URLSearchParams();
      const anyBody: any = body as any;
      if (anyBody?.model) params.set('model', String(anyBody.model));
      if (Array.isArray(anyBody?.messages)) params.set('messages', JSON.stringify(anyBody.messages));
      if (anyBody?.course_name) params.set('course_name', String(anyBody.course_name));
      if (typeof anyBody?.stream !== 'undefined') params.set('stream', String(Boolean(anyBody.stream)));
      if (typeof anyBody?.temperature !== 'undefined') params.set('temperature', String(anyBody.temperature));
      if (typeof anyBody?.retrieval_only !== 'undefined') params.set('retrieval_only', String(Boolean(anyBody.retrieval_only)));

      const headersGet: Record<string, string> = { 'Accept': 'text/event-stream' };
      const maybeKey = (body as any)?.api_key as string | undefined;
      const maybeCourse = (body as any)?.course_name as string | undefined;
      if (maybeKey) {
        headersGet['Authorization'] = `Bearer ${maybeKey}`;
        headersGet['x-api-key'] = maybeKey;
      }
      if (maybeCourse) headersGet['x-course-name'] = maybeCourse;

      for (const base of endpoints) {
        const url = `${base}?${params.toString()}`;
        const upstreamGet = await fetch(url, { method: 'GET', headers: headersGet });
        if (upstreamGet.ok) {
          const contentType = upstreamGet.headers.get('content-type') || 'text/event-stream';
          return new Response(upstreamGet.body, {
            status: upstreamGet.status,
            headers: {
              'Content-Type': contentType,
              'Cache-Control': 'no-cache',
              'Access-Control-Allow-Origin': '*',
            },
          });
        }
        lastStatus = upstreamGet.status;
        lastErrorText = (await upstreamGet.text()) || upstreamGet.statusText;
        if (upstreamGet.status !== 405) break;
      }
    } catch (e) {
      // ignore and fall through to final error
    }

    // If none succeeded, surface the last error with extra context
    return new Response(`UIUC Chat upstream error (${lastStatus}): ${lastErrorText}`, { status: lastStatus });
  } catch (err) {
    // Surface a clearer error message
    const message = err instanceof Error ? err.message : 'Internal server error';
    return new Response(message, { status: 500 });
  }
}
