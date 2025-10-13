const { test, expect } = require('@playwright/test');

test.describe('Passing Tests Suite', () => {
  test('should navigate to example.com', async ({ page }) => {
    await page.goto('https://example.com');
    await expect(page).toHaveTitle(/Example Domain/);
  });

  test('should find heading element', async ({ page }) => {
    await page.goto('https://example.com');
    const heading = page.locator('h1');
    await expect(heading).toBeVisible();
    await expect(heading).toContainText('Example Domain');
  });

  test('should have paragraph text', async ({ page }) => {
    await page.goto('https://example.com');
    const paragraph = page.locator('p').first();
    await expect(paragraph).toBeVisible();
  });

  test('should load page successfully', async ({ page }) => {
    const response = await page.goto('https://example.com');
    expect(response?.status()).toBe(200);
  });

  test('should have correct page structure', async ({ page }) => {
    await page.goto('https://example.com');
    await expect(page.locator('body')).toBeVisible();
    await expect(page.locator('h1')).toBeVisible();
  });
});
