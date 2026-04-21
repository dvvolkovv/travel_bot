export const runtime = 'nodejs';

export async function POST(req: Request) {
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:3001';
  const upstream = await fetch(`${apiBase}/chat/turn`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: await req.text(),
  });
  if (!upstream.body) {
    return new Response('upstream error', { status: 502 });
  }
  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      'content-type': 'text/event-stream',
      'cache-control': 'no-cache',
      connection: 'keep-alive',
    },
  });
}
