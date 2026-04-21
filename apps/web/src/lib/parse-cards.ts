import type { HotelOffer } from '@hotel-deals/shared-types';

const CARDS_BLOCK_RE = /<cards>([\s\S]*?)<\/cards>/;

export function splitCards(text: string): { text: string; offers: HotelOffer[] | null } {
  const match = text.match(CARDS_BLOCK_RE);
  if (!match) return { text, offers: null };
  const before = text.slice(0, match.index);
  const after = text.slice((match.index ?? 0) + match[0].length);
  try {
    const offers = JSON.parse(match[1]) as HotelOffer[];
    return { text: (before + after).trim(), offers };
  } catch {
    return { text, offers: null };
  }
}
