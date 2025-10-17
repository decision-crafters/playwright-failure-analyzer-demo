/**
 * HARD DIFFICULTY FIXES
 *
 * These tests contain complex issues requiring deep understanding of:
 * - Race conditions and timing
 * - State management
 * - Complex async coordination
 * - Edge cases
 *
 * Expected AI Confidence: 50-70%
 * Expected Fix Success Rate: 50-60%
 * Difficulty: ⭐⭐⭐ Hard
 */

const { test, expect } = require('@playwright/test');

test.describe('Hard Fixes - Low Confidence Expected', () => {

  test('complex race condition with multiple navigations', async ({ page }) => {
    // BUG: Multiple async operations without proper coordination
    // Expected fix: Proper Promise.all or sequential awaits with state checks
    // Difficulty: ⭐⭐⭐ Hard - Pattern: race_condition
    await page.goto('https://example.com');
    const link = page.locator('a').first();
    link.click(); // Missing await
    page.goBack(); // Missing await, conflicts with click navigation
    await expect(page.locator('h1')).toHaveText('Example Domain', { timeout: 2000 });
  });

  test('state dependency across multiple interactions', async ({ page }) => {
    // BUG: Assuming state without verifying it
    // Expected fix: Add state verification between steps
    // Difficulty: ⭐⭐⭐ Hard - Pattern: state_assumption
    await page.goto('https://example.com');

    // Clicking a link but not waiting for navigation
    await page.locator('a').first().click();

    // Trying to go back without waiting for forward navigation
    await page.goBack();

    // Expecting original state but timing is unpredictable
    await expect(page).toHaveURL('https://example.com', { timeout: 1000 });
  });

  test('nested async operations with dependencies', async ({ page }) => {
    // BUG: Complex nested operations without proper error boundaries
    // Expected fix: Restructure with proper try/catch and state management
    // Difficulty: ⭐⭐⭐ Hard - Pattern: async_complexity
    await page.goto('https://example.com');

    const links = await page.locator('a').all();
    // Missing: Check if links array is not empty
    const firstLink = links[0];
    const secondLink = links[1]; // May not exist

    await firstLink.click();
    await page.goBack();
    await secondLink.click(); // Will fail if doesn't exist

    await expect(page).toHaveURL(/.*/, { timeout: 2000 });
  });

  test('timing-dependent assertion with side effects', async ({ page }) => {
    // BUG: Multiple operations that depend on precise timing
    // Expected fix: Add explicit waits and state checks
    // Difficulty: ⭐⭐⭐ Hard - Pattern: timing_dependency
    await page.goto('https://example.com');

    await page.locator('a').first().click();
    // Missing: Wait for navigation
    page.goBack(); // Starts immediately, conflicts with navigation
    // Missing: Wait for back navigation

    await expect(page.locator('h1')).toBeVisible({ timeout: 500 });
  });

  test('complex selector chain with conditional logic', async ({ page }) => {
    // BUG: Complex selector without fallback
    // Expected fix: Add existence check or simplify selector
    // Difficulty: ⭐⭐⭐ Hard - Pattern: selector_complexity
    await page.goto('https://example.com');

    // Overly complex selector that may not work
    const element = page
      .locator('div')
      .filter({ has: page.locator('span') })
      .filter({ hasText: 'Nonexistent' })
      .locator('a')
      .first();

    await expect(element).toBeVisible({ timeout: 2000 });
  });

  test('parallel async operations without coordination', async ({ page }) => {
    // BUG: Running multiple async operations that should be sequential
    // Expected fix: Proper sequencing or coordination
    // Difficulty: ⭐⭐⭐ Hard - Pattern: async_coordination
    await page.goto('https://example.com');

    // These operations conflict
    const nav1 = page.locator('a').first().click();
    const nav2 = page.goBack(); // Conflicts with click navigation
    const check = expect(page.locator('h1')).toBeVisible();

    // All running in parallel - unpredictable outcome
    await Promise.all([nav1, nav2, check]);
  });

  test('stateful interaction sequence with missing checks', async ({ page }) => {
    // BUG: Assuming state transitions without verification
    // Expected fix: Add state verification between transitions
    // Difficulty: ⭐⭐⭐ Hard - Pattern: state_verification
    await page.goto('https://example.com');

    // State 1: Click link
    await page.locator('a').first().click();

    // State 2: Back - but not waiting for previous navigation
    page.goBack(); // Missing await

    // State 3: Forward - but previous state not verified
    page.goForward(); // Missing await

    // Expecting specific state but no guarantees
    await expect(page).toHaveURL(/example/, { timeout: 1000 });
  });

  test('error recovery without proper handling', async ({ page }) => {
    // BUG: No error handling for operations that may fail
    // Expected fix: Add try/catch and fallback logic
    // Difficulty: ⭐⭐⭐ Hard - Pattern: error_handling
    await page.goto('https://example.com');

    // This will fail but no error handling
    const nonexistent = page.locator('input[type="email"]');
    await nonexistent.fill('test@example.com', { timeout: 1000 });
    await nonexistent.press('Enter');

    await expect(page).toHaveURL(/.*/, { timeout: 1000 });
  });

  test('multiple conditional paths without validation', async ({ page }) => {
    // BUG: Complex conditional logic with missing validations
    // Expected fix: Add validation and proper branching
    // Difficulty: ⭐⭐⭐ Hard - Pattern: conditional_complexity
    await page.goto('https://example.com');

    const links = page.locator('a');
    const count = await links.count();

    // Assuming count > 0 without checking
    if (count > 0) {
      await links.nth(5).click(); // May not exist
    }

    // Missing: What if count === 0 or nth(5) doesn't exist?
    await expect(page).toHaveURL(/.*/, { timeout: 1000 });
  });

  test('resource loading timing issue', async ({ page }) => {
    // BUG: Not waiting for resources to load before interaction
    // Expected fix: Add proper resource wait or state check
    // Difficulty: ⭐⭐⭐ Hard - Pattern: resource_timing
    await page.goto('https://example.com', { waitUntil: 'commit' });

    // Immediately trying to interact - resources may not be loaded
    const link = page.locator('a').nth(3); // May not be rendered yet
    await link.click({ timeout: 500 });

    await expect(page).toHaveURL(/.*/, { timeout: 1000 });
  });
});
