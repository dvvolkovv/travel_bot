export const runtime = 'nodejs';

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ offerId: string }> },
) {
  const { offerId } = await params;
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:3001';
  return Response.redirect(`${apiBase}/r/${encodeURIComponent(offerId)}`, 302);
}
