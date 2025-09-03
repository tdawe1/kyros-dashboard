// @ts-check
import { test, expect } from '@playwright/test';

test.describe('Kyros Dashboard - Full Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Mock backend APIs to reduce flakiness and remove external deps
    await page.route('**/api/config', route => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ api_mode: 'demo', default_model: 'gpt-4o-mini', apiBaseUrl: 'http://localhost:8000' })
    }));
    await page.route('**/api/kpis', route => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ total_jobs: 0, running: 0, queued: 0 })
    }));
    await page.route('**/api/jobs', route => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([])
    }));
    await page.route('**/api/generate', async route => {
      const response = {
        job_id: 'demo-job',
        variants: {
          linkedin: [
            { id: 'v1', text: 'LinkedIn sample variant content that is sufficiently long for testing.', length: 120, readability: 'Good' }
          ],
          twitter: [
            { id: 'v2', text: 'Twitter sample variant content for testing.', length: 80, readability: 'Fair' }
          ]
        }
      };
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(response) });
    });
    await page.route('**/api/export', route => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ file_url: 'data:text/csv;base64,Y29udGVudA==', filename: 'variants.csv' })
    }));

    // Navigate to the dashboard
    await page.goto('/');

    // Wait for the main page title inside main content
    await expect(page.locator('[data-testid="main-content"] [data-testid="page-title"]').first()).toBeVisible();
  });

  test('complete content generation flow', async ({ page }) => {
    // Step 1: Navigate to Studio page
    await page.click('text=Studio');
    await expect(page).toHaveURL(/.*studio/);

    // Step 2: Paste article content
    const sampleArticle = `
      Artificial intelligence is revolutionizing the way businesses operate in the modern world.
      From machine learning algorithms that power recommendation systems to natural language
      processing that enables chatbots, AI is becoming increasingly integrated into our daily lives.

      Companies are leveraging AI to improve efficiency, reduce costs, and enhance customer
      experiences. However, with these benefits come challenges around ethics, privacy, and
      the future of work. As we continue to develop and deploy AI systems, it's crucial that
      we consider the broader implications and ensure that these technologies are developed
      responsibly and with human welfare in mind.

      The future of AI holds great promise, but it also requires careful consideration of
      the ethical implications and potential risks. Organizations must balance innovation
      with responsibility to ensure that AI technologies benefit society as a whole.
    `;

    const textarea = page.locator('[data-testid="content-input"]');
    await textarea.fill(sampleArticle);

    // Step 3: Ensure channels are selected (idempotent)
    for (const ch of ['linkedin', 'twitter']) {
      const btn = page.locator(`[data-testid="channel-${ch}"]`);
      const className = await btn.getAttribute('class');
      if (!className || !className.includes('bg-blue-600')) {
        await btn.click();
      }
    }

    // Step 4: Set tone (button-based)
    const toneButton = page.locator('[data-testid="tone-professional"]');
    if (await toneButton.isVisible()) {
      await toneButton.click();
    }

    // Step 5: Generate content
    const generateButton = page.locator('[data-testid="generate-button"]');
    await expect(generateButton).toBeEnabled();
    const [resp] = await Promise.all([
      page.waitForResponse(r => r.url().includes('/api/generate') && r.status() === 200, { timeout: 30000 }),
      generateButton.click(),
    ]);
    expect(resp.ok()).toBeTruthy();

    // Step 6: Wait for variants to appear
    await expect(page.locator('[data-testid="variant-card"]').first()).toBeVisible({ timeout: 60000 });

    // Step 7: Verify variants are displayed
    const variantCards = page.locator('[data-testid="variant-card"]');
    const variantCount = await variantCards.count();
    expect(variantCount).toBeGreaterThan(0);

    // Step 8: Select a variant (click accept or select button)
    const firstVariant = variantCards.first();
    const acceptButton = firstVariant.locator('[data-testid="accept-button"]');

    if (await acceptButton.isVisible()) {
      await acceptButton.click();
    } else {
      await firstVariant.click();
    }

    // Step 9: Export functionality (select first variant to reveal bulk export)
    await firstVariant.locator('[data-testid="select-variant"]').check();
    const exportButton = page.locator('[data-testid="export-button"]');
    if (await exportButton.isVisible()) {
      await exportButton.click();
      await expect(exportButton).toBeVisible();
    }
  });

  test('content generation with different channels', async ({ page }) => {
    await page.click('text=Studio');

    const sampleText = 'This is a test article about the latest trends in technology and innovation. '.repeat(3);
    const textarea = page.locator('[data-testid="content-input"]');
    await textarea.fill(sampleText);

    // Test different channel combinations
    const channels = ['linkedin', 'twitter', 'newsletter', 'blog'];

    for (const channel of channels) {
      // Ensure only this channel is selected
      for (const ch of channels) {
        const btn = page.locator(`[data-testid="channel-${ch}"]`);
        const className = await btn.getAttribute('class');
        const isSelected = !!className && className.includes('bg-blue-600');
        if (ch === channel) {
          if (!isSelected) await btn.click();
        } else {
          if (isSelected) await btn.click();
        }
      }

      // Generate content
      const generateButton = page.locator('[data-testid="generate-button"]');
      await expect(generateButton).toBeEnabled();
      const [resp] = await Promise.all([
        page.waitForResponse(r => r.url().includes('/api/generate') && r.status() === 200, { timeout: 30000 }),
        generateButton.click(),
      ]);
      expect(resp.ok()).toBeTruthy();

      // Wait for variants
      await expect(page.locator('[data-testid="variant-card"]').first()).toBeVisible({ timeout: 60000 });

      // Verify channel-specific content
      const variantText = await page.locator('[data-testid="variant-card"]').first().textContent();
      expect(variantText).toBeTruthy();
    }
  });

  test('error handling for invalid input', async ({ page }) => {
    await page.click('text=Studio');

    // Generate button should be disabled for empty input
    const generateButton = page.locator('[data-testid="generate-button"]');
    await expect(generateButton).toBeDisabled();

    // Short input keeps button disabled
    const textarea = page.locator('[data-testid="content-input"]');
    await textarea.fill('Short');
    await expect(generateButton).toBeDisabled();
  });

  test('responsive design on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto('/');

    // Check that mobile navigation works
    const mobileMenuButton = page.locator('[data-testid="mobile-menu"]').first();
    if (await mobileMenuButton.isVisible()) {
      await mobileMenuButton.click();
    }

    // Navigate to Studio
    await page.click('text=Studio');

    // Verify mobile layout
    await expect(page.locator('[data-testid="content-input"]').first()).toBeVisible();
    await expect(page.locator('[data-testid="generate-button"]').first()).toBeVisible();
  });
});
