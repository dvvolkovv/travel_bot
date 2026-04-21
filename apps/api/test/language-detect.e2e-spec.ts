import { detectLang, detectCurrency } from '../src/chat/language-detect';

describe('language-detect', () => {
  it('detects Russian from Cyrillic', () => {
    expect(detectLang('Москва на 3 ночи')).toBe('ru');
  });
  it('defaults to English', () => {
    expect(detectLang('Paris 3 nights')).toBe('en');
  });
  it('detects EUR from € symbol', () => {
    expect(detectCurrency('Barcelona under €600', 'en')).toBe('EUR');
  });
  it('detects RUB from ₽', () => {
    expect(detectCurrency('до 50000 ₽', 'ru')).toBe('RUB');
  });
  it('defaults EN → USD', () => {
    expect(detectCurrency('find hotels', 'en')).toBe('USD');
  });
});
