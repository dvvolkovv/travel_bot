'use client';

import { useTranslations } from 'next-intl';

const KEYS = ['suggestion_cheaper', 'suggestion_closer_center', 'suggestion_higher_rated', 'suggestion_different_dates'] as const;

export function SuggestionChips({ onPick }: { onPick: (text: string) => void }) {
  const t = useTranslations('chat');
  return (
    <div className="flex gap-2 flex-wrap mt-3">
      {KEYS.map((k) => {
        const label = t(k);
        return (
          <button key={k} onClick={() => onPick(label)} className="px-3 py-1 text-sm rounded-full bg-zinc-800 hover:bg-zinc-700">
            {label}
          </button>
        );
      })}
    </div>
  );
}
