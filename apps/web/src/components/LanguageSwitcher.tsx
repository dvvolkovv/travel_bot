'use client';

import { useTranslations } from 'next-intl';
import { useRouter, useParams, usePathname } from 'next/navigation';

export function LanguageSwitcher() {
  const t = useTranslations('nav');
  const router = useRouter();
  const params = useParams() as { locale: string };
  const pathname = usePathname();

  const other = params.locale === 'en' ? 'ru' : 'en';
  const switchTo = () => {
    const newPath = pathname.replace(`/${params.locale}`, `/${other}`);
    router.push(newPath);
  };

  return (
    <button onClick={switchTo} className="text-sm text-zinc-400 hover:text-zinc-100">
      {t('switch_language')}
    </button>
  );
}
