const CYRILLIC = /[А-Яа-яЁё]/;
const CURRENCY_HINTS: Record<string, string> = {
  '₽': 'RUB', 'руб': 'RUB', 'р.': 'RUB',
  '€': 'EUR', 'eur': 'EUR',
  '$': 'USD', 'usd': 'USD',
  '£': 'GBP', 'gbp': 'GBP',
};

export function detectLang(text: string): 'en' | 'ru' {
  return CYRILLIC.test(text) ? 'ru' : 'en';
}

export function detectCurrency(text: string, lang: 'en' | 'ru'): string {
  const lower = text.toLowerCase();
  for (const [hint, code] of Object.entries(CURRENCY_HINTS)) {
    if (lower.includes(hint.toLowerCase())) return code;
  }
  return lang === 'ru' ? 'RUB' : 'USD';
}
