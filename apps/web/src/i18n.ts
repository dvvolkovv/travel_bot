import { getRequestConfig } from 'next-intl/server';
import { notFound } from 'next/navigation';

export const locales = ['en', 'ru'] as const;
export type Locale = (typeof locales)[number];

export default getRequestConfig(async ({ requestLocale }) => {
  const resolved = await requestLocale;
  if (!resolved || !locales.includes(resolved as Locale)) {
    notFound();
  }
  return {
    locale: resolved,
    messages: (await import(`../messages/${resolved}.json`)).default,
  };
});
