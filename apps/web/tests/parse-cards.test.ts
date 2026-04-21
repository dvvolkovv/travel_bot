import { describe, it, expect } from 'vitest';
import { splitCards } from '../src/lib/parse-cards';

describe('splitCards', () => {
  it('extracts cards JSON and leaves remaining text', () => {
    const offer = {
      offer_id: 'abc', hotel_name: 'H', stars: 4, rating: 9, rating_label: 'Great',
      price_per_night_usd: 100,
      price_per_night_original: { amount: 100, currency: 'USD' },
      total_usd: 500, discount_pct: null, original_price_usd: null,
      amenities: [], distance_to_center_km: null, distance_to_beach_km: null,
      photo_url: null, booking_url: 'https://x',
    };
    const input = `Intro text.\n<cards>${JSON.stringify([offer])}</cards>\nAfter.`;
    const out = splitCards(input);
    expect(out.offers).not.toBeNull();
    expect(out.offers?.length).toBe(1);
    expect(out.text).toBe('Intro text.\n\nAfter.');
  });

  it('returns original text if no cards block', () => {
    const out = splitCards('Just text');
    expect(out.offers).toBeNull();
    expect(out.text).toBe('Just text');
  });
});
