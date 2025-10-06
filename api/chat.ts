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

    const upstream = await fetch('https://uiuc.chat/api/chat-api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Some providers require explicit SSE accept header
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify(body),
    });

    if (!upstream.ok) {
      const text = await upstream.text();
      return new Response(text || upstream.statusText, { status: upstream.status });
    }

    // Stream upstream response back to the client.
    // Do not set hop-by-hop headers like 'Connection' in Edge runtime.
    const contentType = upstream.headers.get('content-type') || 'text/event-stream';
    return new Response(upstream.body, {
      status: upstream.status,
      headers: {
        'Content-Type': contentType,
        'Cache-Control': 'no-cache',
        'Access-Control-Allow-Origin': '*'
      },
    });
  } catch (err) {
    // Surface a clearer error message
    const message = err instanceof Error ? err.message : 'Internal server error';
    return new Response(message, { status: 500 });
  }
}
