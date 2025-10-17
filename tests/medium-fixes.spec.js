/**
 * MEDIUM DIFFICULTY FIXES
 *
 * These tests contain timing, state, and coordination issues that require
 * understanding of async patterns and Playwright best practices.
 *
 * Expected AI Confidence: 70-85%
 * Expected Fix Success Rate: 70-80%
 * Difficulty: ⭐⭐ Medium
 */

const { test, expect } = require('@playwright/test');

test.describe('Medium Fixes - Moderate Confidence Expected', () => {

  test('navigation without waiting for load', async ({ page }) => {
    // BUG: Not waiting for navigation to complete before assertions
    // Expected fix: Add waitForLoadState or use proper navigation options
    // Difficulty: ⭐⭐ Medium - Pattern: navigation_timing
    page.goto('https://example.com', { waitUntil: 'commit' }); // Should wait for 'load' or 'networkidle'

    await expect(page.locator('h1')).toBeVisible({ timeout: 2000 });
  });

  test('checking element before it exists', async ({ page }) => {
    await page.goto('https://example.com');

    // BUG: Trying to get attribute immediately without waiting
    // Expected fix: Use expect with toHaveAttribute which auto-waits
    // Difficulty: ⭐⭐ Medium - Pattern: missing_wait
    const link = page.locator('a').first();
    const href = await link.getAttribute('href');
    expect(href).toBeTruthy(); // May fail if element loads slowly
  });

  test('incorrect timeout strategy', async ({ page }) => {
    await page.goto('https://example.com');

    // BUG: Using fixed delay instead of waiting for condition
    // Expected fix: Replace timeout with proper wait
    // Difficulty: ⭐⭐ Medium - Pattern: improper_wait
    await page.waitForTimeout(100); // Should use waitForSelector or similar
    await expect(page.locator('h1')).toBeVisible();
  });

  test('race condition with multiple actions', async ({ page }) => {
    await page.goto('https://example.com');

    // BUG: Not awaiting intermediate step
    // Expected fix: Ensure proper await chain
    // Difficulty: ⭐⭐ Medium - Pattern: missing_await
    const heading = page.locator('h1');
    heading.scrollIntoViewIfNeeded(); // Missing await
    await expect(heading).toBeVisible();
  });

  test('checking wrong state after navigation', async ({ page }) => {
    await page.goto('https://example.com');

    // BUG: Clicking link without waiting for navigation
    // Expected fix: Use Promise.all or waitForURL
    // Difficulty: ⭐⭐ Medium - Pattern: navigation_timing
    const link = page.locator('a').first();
    await link.click();
    // Missing: await page.waitForURL(/.*/)
    await expect(page).toHaveURL('https://example.com', { timeout: 2000 });
  });

  test('selector that needs refinement', async ({ page }) => {
    await page.goto('https://example.com');

    // BUG: Ambiguous selector with filter that doesn't exist
    // Expected fix: Use correct selector or remove invalid filter
    // Difficulty: ⭐⭐ Medium - Pattern: selector_error
    await expect(page.locator('p').filter({ hasText: 'Nonexistent' })).toBeVisible({ timeout: 2000 });
  });

  test('async operation without proper error handling', async ({ page }) => {
    // BUG: Invalid URL format without error handling
    // Expected fix: Use valid URL format
    // Difficulty: ⭐⭐ Medium - Pattern: navigation_error
    await page.goto('invalid-url-format', { timeout: 2000 });
    await expect(page.locator('h1')).toBeVisible();
  });

  test('element interaction before ready', async ({ page }) => {
    await page.goto('https://example.com');

    // BUG: Typing into element that might not be ready
    // Expected fix: Ensure element is visible/enabled first
    // Difficulty: ⭐⭐ Medium - Pattern: element_not_ready
    const input = page.locator('input'); // No input exists on example.com
    await input.fill('text', { timeout: 2000 });
  });

  test('multiple assertions without proper waits', async ({ page }) => {
    await page.goto('https://example.com');

    // BUG: Chaining assertions without ensuring state
    // Expected fix: Add proper waits between state changes
    // Difficulty: ⭐⭐ Medium - Pattern: assertion_timing
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('h1')).toHaveText('Wrong Text', { timeout: 1000 });
  });

  test('navigation with incorrect wait strategy', async ({ page }) => {
    // BUG: Using goto without await
    // Expected fix: Add await and proper waitUntil option
    // Difficulty: ⭐⭐ Medium - Pattern: navigation_timing
    page.goto('https://example.com', { waitUntil: 'domcontentloaded' });

    await expect(page.locator('body')).toBeVisible({ timeout: 2000 });
  });
});
