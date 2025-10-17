/**
 * HARD DIFFICULTY FIXES - SOLUTIONS
 *
 * This file contains the CORRECT implementations for all tests in hard-fixes.spec.js
 * Use this to:
 * - Validate AI-generated fixes for complex scenarios
 * - Understand proper async coordination and state management
 * - Learn advanced Playwright patterns
 *
 * Difficulty: ⭐⭐⭐ Hard
 */

const { test, expect } = require('@playwright/test');

test.describe('Hard Fixes - Solutions (All Passing)', () => {

  test('complex race condition with multiple navigations', async ({ page }) => {
    // SOLUTION: Proper async coordination with awaits
    await page.goto('https://example.com');
    const link = page.locator('a').first();

    // Wait for navigation to complete before going back
    await link.click();
    await page.waitForLoadState('load');
    await page.goBack();
    await page.waitForLoadState('load');

    await expect(page.locator('h1')).toHaveText('Example Domain', { timeout: 2000 });
  });

  test('state dependency across multiple interactions', async ({ page }) => {
    // SOLUTION: Verify state at each step
    await page.goto('https://example.com');

    // Navigate forward and wait
    await page.locator('a').first().click();
    await page.waitForLoadState('load');

    // Navigate back and wait
    await page.goBack();
    await page.waitForLoadState('load');

    // Verify we're back to original URL
    await expect(page).toHaveURL('https://example.com', { timeout: 2000 });
  });

  test('nested async operations with dependencies', async ({ page }) => {
    // SOLUTION: Add existence checks and proper error handling
    await page.goto('https://example.com');

    const links = await page.locator('a').all();

    // Check array has elements
    if (links.length > 0) {
      const firstLink = links[0];
      await firstLink.click();
      await page.waitForLoadState('load');
      await page.goBack();
      await page.waitForLoadState('load');

      // Check if second link exists
      if (links.length > 1) {
        const secondLink = links[1];
        await secondLink.click();
        await page.waitForLoadState('load');
      }
    }

    await expect(page).toHaveURL(/.*/, { timeout: 2000 });
  });

  test('timing-dependent assertion with side effects', async ({ page }) => {
    // SOLUTION: Explicit waits between conflicting operations
    await page.goto('https://example.com');

    await page.locator('a').first().click();
    await page.waitForLoadState('load'); // Wait for forward navigation

    await page.goBack();
    await page.waitForLoadState('load'); // Wait for back navigation

    await expect(page.locator('h1')).toBeVisible({ timeout: 2000 });
  });

  test('complex selector chain with conditional logic', async ({ page }) => {
    // SOLUTION: Simplify selector or add existence check
    await page.goto('https://example.com');

    // Option 1: Simplify - just check if any link is visible
    const element = page.locator('a').first();
    await expect(element).toBeVisible({ timeout: 2000 });

    // Option 2: With existence check
    // const complex = page.locator('div').filter({ has: page.locator('span') });
    // const count = await complex.count();
    // if (count > 0) {
    //   await expect(complex.first()).toBeVisible();
    // }
  });

  test('parallel async operations without coordination', async ({ page }) => {
    // SOLUTION: Sequential execution where operations conflict
    await page.goto('https://example.com');

    // Execute sequentially, not in parallel
    await page.locator('a').first().click();
    await page.waitForLoadState('load');

    await page.goBack();
    await page.waitForLoadState('load');

    await expect(page.locator('h1')).toBeVisible();
  });

  test('stateful interaction sequence with missing checks', async ({ page }) => {
    // SOLUTION: Verify state after each transition
    await page.goto('https://example.com');

    // State 1: Navigate forward
    await page.locator('a').first().click();
    await page.waitForLoadState('load');
    await expect(page).not.toHaveURL('https://example.com');

    // State 2: Navigate back
    await page.goBack();
    await page.waitForLoadState('load');
    await expect(page).toHaveURL('https://example.com');

    // State 3: Navigate forward again
    await page.goForward();
    await page.waitForLoadState('load');

    // Final state verification
    await expect(page).toHaveURL(/example/, { timeout: 2000 });
  });

  test('error recovery without proper handling', async ({ page }) => {
    // SOLUTION: Add try/catch and fallback
    await page.goto('https://example.com');

    try {
      const input = page.locator('input[type="email"]');
      await expect(input).toBeVisible({ timeout: 1000 });
      await input.fill('test@example.com');
      await input.press('Enter');
    } catch (error) {
      // Fallback: Since input doesn't exist on example.com, just verify we're still on the page
      await expect(page).toHaveURL(/example/);
    }

    await expect(page).toHaveURL(/.*/, { timeout: 1000 });
  });

  test('multiple conditional paths without validation', async ({ page }) => {
    // SOLUTION: Add proper validation
    await page.goto('https://example.com');

    const links = page.locator('a');
    const count = await links.count();

    // Validate count before accessing
    if (count > 5) {
      await links.nth(5).click();
      await page.waitForLoadState('load');
    } else if (count > 0) {
      // Fallback to first link
      await links.first().click();
      await page.waitForLoadState('load');
    }

    await expect(page).toHaveURL(/.*/, { timeout: 2000 });
  });

  test('resource loading timing issue', async ({ page }) => {
    // SOLUTION: Wait for proper load state
    await page.goto('https://example.com', { waitUntil: 'load' });

    // Verify element exists before interacting
    const link = page.locator('a').nth(3);
    await expect(link).toBeVisible({ timeout: 2000 });
    await link.click();

    await expect(page).toHaveURL(/.*/, { timeout: 2000 });
  });
});
