const { test, expect } = require('@playwright/test');

test.describe('Intentional Failure Tests', () => {
  test('timeout failure - element not found', async ({ page }) => {
    await page.goto('https://example.com');
    await expect(page.locator('#non-existent-element')).toBeVisible({
      timeout: 2000
    });
  });

  test('assertion failure - wrong title', async ({ page }) => {
    await page.goto('https://example.com');
    const title = await page.title();
    expect(title).toBe('Wrong Title Expected');
  });

  test('navigation timeout - invalid domain', async ({ page }) => {
    await page.goto('https://this-domain-definitely-does-not-exist-12345.com', {
      timeout: 3000
    });
  });

  test('selector not found - click failure', async ({ page }) => {
    await page.goto('https://example.com');
    await page.click('#nonexistent-button', { timeout: 2000 });
  });

  test('text content mismatch', async ({ page }) => {
    await page.goto('https://example.com');
    await expect(page.locator('h1')).toHaveText('This Text Does Not Exist');
  });
});
