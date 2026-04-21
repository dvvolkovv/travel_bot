'use client';

import type { HotelOffer } from '@hotel-deals/shared-types';
import { useTranslations, useFormatter } from 'next-intl';

export function HotelCard({ offer, nights }: { offer: HotelOffer; nights: number }) {
  const t = useTranslations('card');
  const fmt = useFormatter();
  const currency = offer.price_per_night_original.currency;
  const price = offer.price_per_night_original.amount;

  return (
    <article className="rounded-2xl overflow-hidden bg-zinc-900 border border-zinc-800">
      {offer.photo_url && (
        <img src={offer.photo_url} alt={offer.hotel_name} className="w-full h-48 object-cover" />
      )}
      <div className="p-4 space-y-3">
        <div>
          <h3 className="font-semibold text-lg">{offer.hotel_name}</h3>
          <div className="text-sm text-zinc-400">
            {'★'.repeat(Math.max(0, Math.min(5, offer.stars)))} · {offer.rating.toFixed(1)} {offer.rating_label}
            {offer.distance_to_beach_km !== null && (
              <span> · {t('distance_beach', { km: offer.distance_to_beach_km })}</span>
            )}
            {offer.distance_to_beach_km === null && offer.distance_to_center_km !== null && (
              <span> · {t('distance_center', { km: offer.distance_to_center_km })}</span>
            )}
          </div>
        </div>

        {offer.amenities.length > 0 && (
          <div className="flex gap-2 flex-wrap text-xs">
            {offer.amenities.slice(0, 3).map((a) => (
              <span key={a} className="px-2 py-1 rounded bg-zinc-800">
                ✓ {a}
              </span>
            ))}
          </div>
        )}

        <div>
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-semibold">
              {fmt.number(Number(price), { style: 'currency', currency })}
            </span>
            <span className="text-sm text-zinc-400">{t('per_night')}</span>
            {offer.discount_pct && (
              <span className="text-sm text-emerald-400">{t('discount', { pct: offer.discount_pct })}</span>
            )}
          </div>
          <div className="text-sm text-zinc-400">
            {t('total', { nights })}: {fmt.number(Number(price) * nights, { style: 'currency', currency })}
          </div>
        </div>

        <a
          href={`/r/${offer.offer_id}`}
          className="block text-center py-2 rounded-lg bg-blue-600 hover:bg-blue-500 font-medium"
          data-testid="book-button"
        >
          {t('book_now')}
        </a>
      </div>
    </article>
  );
}
