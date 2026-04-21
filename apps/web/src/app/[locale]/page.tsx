'use client';

import { useTranslations } from 'next-intl';
import { useRouter, useParams } from 'next/navigation';
import { nanoid } from 'nanoid';
import { useState } from 'react';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';

export default function HomePage() {
  const t = useTranslations('landing');
  const router = useRouter();
  const { locale } = useParams() as { locale: string };
  const [text, setText] = useState('');

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    const sid = nanoid();
    document.cookie = `session_id=${sid}; path=/; max-age=7200`;
    router.push(`/${locale}/c/${sid}?q=${encodeURIComponent(text)}`);
  };

  return (
    <main className="max-w-2xl mx-auto px-6 py-16">
      <div className="flex justify-end mb-8"><LanguageSwitcher /></div>
      <h1 className="text-4xl font-bold mb-4">{t('hero.title')}</h1>
      <p className="text-zinc-400 mb-8">{t('hero.subtitle')}</p>
      <form onSubmit={submit} className="space-y-3">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={t('hero.placeholder')}
          rows={3}
          className="w-full rounded-lg bg-zinc-900 border border-zinc-800 p-4"
          autoFocus
        />
        <button type="submit" className="px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 font-medium">
          {t('hero.submit')}
        </button>
      </form>
    </main>
  );
}
