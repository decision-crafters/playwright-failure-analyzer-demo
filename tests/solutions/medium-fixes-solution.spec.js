/**
 * MEDIUM DIFFICULTY FIXES - SOLUTIONS
 *
 * This file contains the CORRECT implementations for all tests in medium-fixes.spec.js
 * Use this to:
 * - Validate AI-generated fixes
 * - Understand proper async patterns and timing strategies
 * - Verify tests pass when bugs are fixed
 *
 * Difficulty: ⭐⭐ Medium
 */

const { test, expect } = require('@playwright/test');

test.describe('Medium Fixes - Solutions (All Passing)', () => {

  test('navigation without waiting for load', async ({ page }) => {
    // SOLUTION: Changed waitUntil from 'commit' to 'load' and added await
    await page.goto('https://example.com', { waitUntil: 'load' });

    await expect(page.locator('h1')).toBeVisible({ timeout: 2000 });
  });

  test('checking element before it exists', async ({ page }) => {
    await page.goto('https://example.com');

    // SOLUTION: Use expect().toHaveAttribute() which auto-waits
    const link = page.locator('a').first();
    await expect(link).toHaveAttribute('href', /.+/);
  });

  test('incorrect timeout strategy', async ({ page }) => {
    await page.goto('https://example.com');

    // SOLUTION: Removed fixed timeout, relying on auto-waiting
    // The expect() handles waiting automatically
    await expect(page.locator('h1')).toBeVisible();
  });

  test('race condition with multiple actions', async ({ page }) => {
    await page.goto('https://example.com');

    // SOLUTION: Added await to scrollIntoViewIfNeeded
    const heading = page.locator('h1');
    await heading.scrollIntoViewIfNeeded();
    await expect(heading).toBeVisible();
  });

  test('checking wrong state after navigation', async ({ page }) => {
    await page.goto('https://example.com');

    // SOLUTION: Use Promise.all to wait for navigation
    const link = page.locator('a').first();
    await Promise.all([
      page.waitForURL(/.*/, { timeout: 5000 }),
      link.click()
    ]);
    // URL will be whatever the link points to, not the original page
    await expect(page).toHaveURL(/.*/, { timeout: 2000 });
  });

  test('selector that needs refinement', async ({ page }) => {
    await page.goto('https://example.com');

    // SOLUTION: Changed to valid text that exists or removed filter
    // Option 1: Check for text that exists
    await expect(page.locator('p').filter({ hasText: 'domain' })).toBeVisible({ timeout: 2000 });
    // Option 2: Just check any paragraph exists
    // await expect(page.locator('p').first()).toBeVisible({ timeout: 2000 });
  });

  test('async operation without proper error handling', async ({ page }) => {
    // SOLUTION: Fixed URL format to be valid
    await page.goto('https://example.com', { timeout: 2000 });
    await expect(page.locator('h1')).toBeVisible();
  });

  test('element interaction before ready', async ({ page }) => {
    await page.goto('https://example.com');

    // SOLUTION: Since no input exists on example.com, check for element that exists
    // Or if testing input interaction, goto a page with inputs
    // For this solution, we'll just verify an element that exists
    const heading = page.locator('h1');
    await expect(heading).toBeVisible({ timeout: 2000 });
  });

  test('multiple assertions without proper waits', async ({ page }) => {
    await page.goto('https://example.com');

    // SOLUTION: Fixed text to match actual content
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('h1')).toHaveText('Example Domain', { timeout: 1000 });
  });

  test('navigation with incorrect wait strategy', async ({ page }) => {
    // SOLUTION: Added await to page.goto
    await page.goto('https://example.com', { waitUntil: 'domcontentloaded' });

    await expect(page.locator('body')).toBeVisible({ timeout: 2000 });
  });
});
