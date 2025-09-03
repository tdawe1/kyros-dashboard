// @ts-check
import { test, expect } from '@playwright/test';

test.describe('Kyros Dashboard - Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('[data-testid="page-title"]').first()).toBeVisible();
  });

  test('navigation between main pages', async ({ page }) => {
    // Prefer sidebar links if available
    const sidebar = page.locator('[data-testid="sidebar"]');

    const navClick = async (label) => {
      const candidates = [label, label === 'Jobs' ? 'Job Monitor' : null].filter(Boolean);
      for (const candidate of candidates) {
        if (await sidebar.isVisible()) {
          const link = sidebar.locator(`text=${candidate}, a:has-text("${candidate}")`).first();
          if (await link.isVisible()) {
            await link.click();
            return true;
          }
        }
        const pageLink = page.locator(`text=${candidate}`).first();
        if (await pageLink.isVisible()) {
          await pageLink.click();
          return true;
        }
      }
      return false;
    };

    // Dashboard
    await navClick('Dashboard');
    await expect(page).toHaveURL(/.*dashboard|.*\/$/);
    await expect(page.locator('[data-testid="page-title"]').first()).toBeVisible();

    // Studio
    await navClick('Studio');
    await expect(page).toHaveURL(/.*studio/);
    await expect(page.locator('[data-testid="content-input"]').first()).toBeVisible();

    // Jobs
    await navClick('Jobs');
    await expect(page).toHaveURL(/.*jobs/);
    await expect(page.locator('[data-testid="jobs-table"]').first()).toBeVisible();

    // Settings
    await navClick('Settings');
    await expect(page).toHaveURL(/.*settings/);
    await expect(page.locator('[data-testid="page-title"]').first()).toBeVisible();
  });

  test('sidebar navigation', async ({ page }) => {
    // Check if sidebar exists
    const sidebar = page.locator('[data-testid="sidebar"]');

    if (await sidebar.isVisible()) {
      // Test sidebar navigation items
      const navItems = ['Dashboard', 'Studio', 'Jobs', 'Settings'];

      for (const item of navItems) {
        const candidate = item === 'Jobs' ? 'Job Monitor' : item;
        const navLink = sidebar.locator(`text=${candidate}, a:has-text("${candidate}")`).first();
        if (await navLink.isVisible()) {
          await navLink.click();
          await expect(page.locator('[data-testid="page-title"]').first()).toBeVisible();
        }
      }
    }
  });

  test('theme toggle functionality', async ({ page }) => {
    // Look for theme toggle button
    const themeToggle = page.locator('[data-testid="theme-toggle"]');

    if (await themeToggle.isVisible()) {
      // Get initial theme
      const initialTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme') ||
        (document.documentElement.classList.contains('dark') ? 'dark' : 'light'));

      // Toggle theme
      await themeToggle.click();

      // Wait for theme change
      await page.waitForTimeout(500);

      // Check if theme changed
      const newTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme') ||
        (document.documentElement.classList.contains('dark') ? 'dark' : 'light'));

      expect(newTheme).not.toBe(initialTheme);
    }
  });

  test('mobile navigation menu', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Look for mobile menu button
    const mobileMenuButton = page.locator('[data-testid="mobile-menu"]');

    if (await mobileMenuButton.isVisible()) {
      // Open mobile menu
      await mobileMenuButton.click();

      // Check if menu is open
      const mobileMenu = page.locator('[data-testid="sidebar"], .mobile-menu, nav[aria-expanded="true"]').first();
      await expect(mobileMenu).toBeVisible();

      // Test navigation in mobile menu
      const navItems = ['Dashboard', 'Studio', 'Jobs', 'Settings'];

      for (const item of navItems) {
        const candidate = item === 'Jobs' ? 'Job Monitor' : item;
        const navLink = mobileMenu.locator(`text=${candidate}, a:has-text("${candidate}")`).first();
        if (await navLink.isVisible()) {
          await navLink.click();
          await expect(page.locator('[data-testid="page-title"]').first()).toBeVisible();
          break; // Just test one navigation to avoid too many page changes
        }
      }
    }
  });

  test('breadcrumb navigation', async ({ page }) => {
    // Navigate to a sub-page
    await page.click('text=Studio');

    // Look for breadcrumbs
    const breadcrumbs = page.locator('[data-testid="breadcrumbs"], .breadcrumbs, nav[aria-label*="breadcrumb"]').first();

    if (await breadcrumbs.isVisible()) {
      // Check if breadcrumbs show current page
      await expect(breadcrumbs).toContainText('Studio');

      // Test clicking on breadcrumb items
      const breadcrumbLinks = breadcrumbs.locator('a');
      const linkCount = await breadcrumbLinks.count();

      if (linkCount > 0) {
        // Click on first breadcrumb link (usually home)
        await breadcrumbLinks.first().click();
        await expect(page).toHaveURL(/.*dashboard|.*\/$/);
      }
    }
  });

  test('keyboard navigation', async ({ page }) => {
    // Test Tab navigation
    await page.keyboard.press('Tab');

    // Check if focus is visible
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();

    // Test Enter key on focused element
    await page.keyboard.press('Enter');

    // Test Escape key (should close modals/menus)
    await page.keyboard.press('Escape');
  });

  test('page loading states', async ({ page }) => {
    // Test that pages load without errors
    const pages = [
      { name: 'Dashboard', url: '/' },
      { name: 'Studio', url: '/studio' },
      { name: 'Jobs', url: '/jobs' },
      { name: 'Settings', url: '/settings' }
    ];

    for (const pageInfo of pages) {
      await page.goto(pageInfo.url);

      // Wait for page to load
      await page.waitForLoadState('networkidle');

      // Check for error messages
      const errorMessages = page.locator('text=Error, text=Failed, text=404, text=500').first();
      if (await errorMessages.isVisible()) {
        console.warn(`Error found on ${pageInfo.name} page`);
      }

      // Check that main content is visible
      await expect(page.locator('[data-testid="main-content"]').first()).toBeVisible();
    }
  });
});
