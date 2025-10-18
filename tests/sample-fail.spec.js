const { test, expect } = require('@playwright/test');

test.describe('Intentional Failure Tests', () => {
  test('timeout failure - element not found', async ({ page }) => {
    await page.goto('https://example.com');
await expect(page.locator('h1')).toBeVisible()
      timeout: 2000
    });
  });

  test('assertion failure - wrong title', async ({ page }) => {
    await page.goto('https://example.com');
    const title = await page.title();
expect(title).toBe('Example Domain')
  });

  test('navigation timeout - invalid domain', async ({ page }) => {
await page.goto('https://example.com', { timeout: 10000 })
      timeout: 3000
    });
  });

  test('selector not found - click failure', async ({ page }) => {
    await page.goto('https://example.com');
await page.waitForSelector('#nonexistent-button', { timeout: 5000 }); await page.click('#nonexistent-button');
  });

  test('text content mismatch', async ({ page }) => {
    await page.goto('https://example.com');
await expect(page.locator('h1')).toHaveText('Example Domain', { timeout: 10000 });
  });
});
