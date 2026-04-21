import { test, expect } from '@playwright/test';

test('search Barcelona → see cards → click book', async ({ page }) => {
  await page.goto('/');
  // Landing page: find the textarea (placeholder localized to EN or RU)
  const input = page.getByPlaceholder(/Barcelona|Барселона/i);
  await input.fill('Barcelona 5 nights June 10-15 2026 under €600');
  await page.getByRole('button', { name: /Search|Искать|→/ }).click();

  // Chat page: wait for at least one hotel card to render (timeout generous — live scrape + LLM)
  await expect(page.getByTestId('hotel-card').first()).toBeVisible({ timeout: 45_000 });
  const cardCount = await page.getByTestId('hotel-card').count();
  expect(cardCount).toBeGreaterThanOrEqual(3);

  // Click the first book button → should navigate through /r/<id> → 302 → Booking.com
  const [resp] = await Promise.all([
    page.waitForResponse((r) => r.url().includes('/r/')),
    page.getByTestId('book-button').first().click(),
  ]);
  expect([200, 302]).toContain(resp.status());
});
