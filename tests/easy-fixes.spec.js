/**
 * EASY DIFFICULTY FIXES
 *
 * These tests contain simple, obvious errors that AI models should fix
 * with high confidence (90%+). Perfect for:
 * - Testing basic AI model capabilities
 * - Validating confidence scoring
 * - Quick wins for auto-fix workflows
 *
 * Expected AI Confidence: 90-95%
 * Expected Fix Success Rate: 95%+
 * Difficulty: ⭐ Easy
 */

const { test, expect } = require('@playwright/test');

test.describe('Easy Fixes - High Confidence Expected', () => {

  test('missing await on click action', async ({ page }) => {
    await page.goto('https://example.com');

    // BUG: Missing await keyword (very obvious)
    // Expected fix: Add 'await' before page.click()
    // Difficulty: ⭐ Easy - Pattern: missing_await
    page.click('a'); // Should be: await page.click('a');

    await expect(page).toHaveURL(/.*example.*/);
  });

  test('simple selector typo', async ({ page }) => {
    await page.goto('https://example.com');

    // BUG: Typo in selector - 'h11' should be 'h1'
    // Expected fix: Change 'h11' to 'h1'
    // Difficulty: ⭐ Easy - Pattern: selector_timeout
    await expect(page.locator('h11')).toBeVisible({ timeout: 2000 });
  });

  test('wrong text assertion value', async ({ page }) => {
    await page.goto('https://example.com');

    // BUG: Wrong expected text - page says "Example Domain" not "Example Page"
    // Expected fix: Change "Example Page" to "Example Domain"
    // Difficulty: ⭐ Easy - Pattern: assertion_mismatch
    await expect(page.locator('h1')).toHaveText('Example Page', { timeout: 2000 });
  });

  test('missing await on navigation', async ({ page }) => {
    // BUG: Missing await on goto
    // Expected fix: Add 'await' before page.goto()
    // Difficulty: ⭐ Easy - Pattern: missing_await
    page.goto('https://example.com'); // Should be: await page.goto()

    await expect(page.locator('h1')).toBeVisible();
  });

  test('incorrect boolean assertion', async ({ page }) => {
    await page.goto('https://example.com');

    // BUG: Using toBeVisible on an element that exists but checking for false
    // Expected fix: Remove the '.not' or check a non-existent element
    // Difficulty: ⭐ Easy - Pattern: assertion_mismatch
    await expect(page.locator('h1')).not.toBeVisible({ timeout: 2000 });
  });

  test('simple attribute typo', async ({ page }) => {
    await page.goto('https://example.com');

    // BUG: Checking wrong attribute - 'hreff' should be 'href'
    // Expected fix: Change 'hreff' to 'href'
    // Difficulty: ⭐ Easy - Pattern: selector_timeout
    await expect(page.locator('a')).toHaveAttribute('hreff', /.+/, { timeout: 2000 });
  });

  test('missing await on wait operation', async ({ page }) => {
    await page.goto('https://example.com');

    // BUG: Missing await on waitForSelector
    // Expected fix: Add 'await' before page.waitForSelector()
    // Difficulty: ⭐ Easy - Pattern: missing_await
    page.waitForSelector('h1'); // Should be: await page.waitForSelector('h1')

    await expect(page.locator('p')).toBeVisible();
  });

  test('wrong number in timeout', async ({ page }) => {
    await page.goto('https://example.com');

    // BUG: Unreasonably short timeout (1ms)
    // Expected fix: Increase timeout to reasonable value (e.g., 2000ms)
    // Difficulty: ⭐ Easy - Pattern: timeout_too_short
    await expect(page.locator('h1')).toBeVisible({ timeout: 1 });
  });
});
