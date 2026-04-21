'use client';

import { useState, useRef, useEffect } from 'react';
import { useTranslations } from 'next-intl';

export function ChatInput({ onSubmit, disabled }: { onSubmit: (text: string) => void; disabled: boolean }) {
  const t = useTranslations('landing');
  const [text, setText] = useState('');
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => { if (!disabled) ref.current?.focus(); }, [disabled]);

  const submit = () => {
    const trimmed = text.trim();
    if (!trimmed) return;
    onSubmit(trimmed);
    setText('');
  };

  return (
    <form onSubmit={(e) => { e.preventDefault(); submit(); }} className="flex gap-2">
      <textarea
        ref={ref}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(); } }}
        placeholder={t('hero.placeholder')}
        rows={1}
        disabled={disabled}
        className="flex-1 rounded-lg bg-zinc-900 border border-zinc-800 p-3 resize-none disabled:opacity-50"
      />
      <button type="submit" disabled={disabled} className="px-6 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50">
        →
      </button>
    </form>
  );
}
