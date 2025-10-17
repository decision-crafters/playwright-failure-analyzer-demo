/**
 * EASY DIFFICULTY FIXES - SOLUTIONS
 *
 * This file contains the CORRECT implementations for all tests in easy-fixes.spec.js
 * Use this to:
 * - Validate AI-generated fixes
 * - Understand what the expected fix should be
 * - Verify tests pass when bugs are fixed
 *
 * Difficulty: ⭐ Easy
 */

const { test, expect } = require('@playwright/test');

test.describe('Easy Fixes - Solutions (All Passing)', () => {

  test('missing await on click action', async ({ page }) => {
    await page.goto('https://example.com');

    // SOLUTION: Added 'await' before page.click()
    await page.click('a');

    await expect(page).toHaveURL(/.*example.*/);
  });

  test('simple selector typo', async ({ page }) => {
    await page.goto('https://example.com');

    // SOLUTION: Changed 'h11' to 'h1'
    await expect(page.locator('h1')).toBeVisible({ timeout: 2000 });
  });

  test('wrong text assertion value', async ({ page }) => {
    await page.goto('https://example.com');

    // SOLUTION: Changed "Example Page" to "Example Domain"
    await expect(page.locator('h1')).toHaveText('Example Domain', { timeout: 2000 });
  });

  test('missing await on navigation', async ({ page }) => {
    // SOLUTION: Added 'await' before page.goto()
    await page.goto('https://example.com');

    await expect(page.locator('h1')).toBeVisible();
  });

  test('incorrect boolean assertion', async ({ page }) => {
    await page.goto('https://example.com');

    // SOLUTION: Removed '.not' - h1 is visible on the page
    await expect(page.locator('h1')).toBeVisible({ timeout: 2000 });
  });

  test('simple attribute typo', async ({ page }) => {
    await page.goto('https://example.com');

    // SOLUTION: Changed 'hreff' to 'href'
    await expect(page.locator('a')).toHaveAttribute('href', /.+/, { timeout: 2000 });
  });

  test('missing await on wait operation', async ({ page }) => {
    await page.goto('https://example.com');

    // SOLUTION: Added 'await' before page.waitForSelector()
    await page.waitForSelector('h1');

    await expect(page.locator('p')).toBeVisible();
  });

  test('wrong number in timeout', async ({ page }) => {
    await page.goto('https://example.com');

    // SOLUTION: Increased timeout from 1ms to 2000ms
    await expect(page.locator('h1')).toBeVisible({ timeout: 2000 });
  });
});
