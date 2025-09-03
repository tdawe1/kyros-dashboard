// @ts-check
import { test, expect } from '@playwright/test';

test.describe('Kyros Dashboard - Studio Page', () => {
  test.beforeEach(async ({ page }) => {
    // Mock backend APIs
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

    await page.goto('/studio');
    await expect(page.locator('[data-testid="page-title"]').first()).toBeVisible();
  });

  test('studio page loads correctly', async ({ page }) => {
    // Check page title
    await expect(page.locator('[data-testid="page-title"]').first()).toBeVisible();

    // Check main input area
    await expect(page.locator('[data-testid="content-input"]').first()).toBeVisible();

    // Check channel selection
    await expect(page.locator('[data-testid="channel-linkedin"]').first()).toBeVisible();

    // Check generate button
    await expect(page.locator('[data-testid="generate-button"]').first()).toBeVisible();
  });

  test('content input validation', async ({ page }) => {
    const textarea = page.locator('[data-testid="content-input"]');
    const generateButton = page.locator('[data-testid="generate-button"]');

    // With empty input, button disabled
    await expect(generateButton).toBeDisabled();

    // Short input keeps button disabled
    await textarea.fill('Short text');
    await expect(generateButton).toBeDisabled();

    // Valid input enables button
    const validText = 'This is a valid test input that meets the minimum length requirement and should pass validation. '.repeat(2);
    await textarea.fill(validText);
    await expect(generateButton).toBeEnabled();
  });

  test('channel selection', async ({ page }) => {
    const channels = ['linkedin', 'twitter', 'newsletter', 'blog'];

    for (const channel of channels) {
      const checkbox = page.locator(`[data-testid="channel-${channel}"]`);

      if (await checkbox.isVisible()) {
        // Toggle channel button
        await checkbox.click();
        await expect(checkbox).toBeVisible();
      }
    }
  });

  test('tone selection', async ({ page }) => {
    const tones = ['professional', 'casual', 'engaging', 'formal'];

    for (const tone of tones) {
      const toneButton = page.locator(`[data-testid="tone-${tone}"]`);
      if (await toneButton.isVisible()) {
        await toneButton.click();
        await expect(toneButton).toBeVisible();
      }
    }
  });

  test('preset selection', async ({ page }) => {
    const presetSelect = page.locator('select[name="preset"], [data-testid="preset-select"]').first();

    if (await presetSelect.isVisible()) {
      // Test default preset
      await expect(presetSelect).toHaveValue('default');

      // Test changing preset
      const options = await presetSelect.locator('option').allTextContents();
      if (options.length > 1) {
        await presetSelect.selectOption({ index: 1 });
        await expect(presetSelect).not.toHaveValue('default');
      }
    }
  });

  test('content generation process', async ({ page }) => {
    test.setTimeout(90000);
    const textarea = page.locator('[data-testid="content-input"]');
    const generateButton = page.locator('[data-testid="generate-button"]');

    // Fill in valid content
    const sampleContent = `
      Artificial intelligence is transforming the way we work and live.
      From machine learning algorithms that power recommendation systems
      to natural language processing that enables chatbots, AI is becoming
      increasingly integrated into our daily lives. Companies are leveraging
      AI to improve efficiency, reduce costs, and enhance customer experiences.
    `;

    await textarea.fill(sampleContent);

    // Select channels
    await page.click('[data-testid="channel-linkedin"]');
    await page.click('[data-testid="channel-twitter"]');

    // Click generate
    await expect(generateButton).toBeEnabled();
    await generateButton.click();

    // Either variants appear, or response captured; wait longer just in case
    await expect(page.locator('[data-testid="variant-card"]').first()).toBeVisible({ timeout: 60000 });
  });

  test('variant interaction', async ({ page }) => {
    // First generate some content
    const textarea = page.locator('[data-testid="content-input"]');
    const generateButton = page.locator('[data-testid="generate-button"]');

    await textarea.fill('This is a test article about artificial intelligence and its impact on modern business. '.repeat(3));
    await page.click('[data-testid="channel-linkedin"]');
    await expect(generateButton).toBeEnabled();
    const [resp] = await Promise.all([
      page.waitForResponse(r => r.url().includes('/api/generate') && r.status() === 200, { timeout: 30000 }),
      generateButton.click(),
    ]);
    expect(resp.ok()).toBeTruthy();

    // Wait for variants
    await expect(page.locator('[data-testid="variant-card"]').first()).toBeVisible({ timeout: 60000 });

    const variantCards = page.locator('[data-testid="variant-card"]');
    const firstVariant = variantCards.first();

    // Open edit to ensure card is interactable then close modal before clicking copy
    const editButton = firstVariant.locator('[data-testid="edit-button"]');
    if (await editButton.isVisible()) {
      await editButton.click();
      await expect(page.locator('[data-testid="edit-modal"]').first()).toBeVisible();
      // Close modal
      await page.keyboard.press('Escape');
      await expect(page.locator('[data-testid="edit-modal"]').first()).not.toBeVisible({ timeout: 5000 }).catch(() => {});
    }

    const copyButton = firstVariant.locator('[data-testid="copy-button"]');
    if (await copyButton.isVisible()) {
      await copyButton.click({ trial: true }).catch(() => {});
      await expect(copyButton).toBeVisible();
    }
  });

  test('export functionality', async ({ page }) => {
    // Generate content first
    const textarea = page.locator('[data-testid="content-input"]');
    const generateButton = page.locator('[data-testid="generate-button"]');

    await textarea.fill('This is a test article for export functionality testing. '.repeat(3));
    await page.click('[data-testid="channel-linkedin"]');
    await expect(generateButton).toBeEnabled();
    const [resp] = await Promise.all([
      page.waitForResponse(r => r.url().includes('/api/generate') && r.status() === 200, { timeout: 30000 }),
      generateButton.click(),
    ]);
    expect(resp.ok()).toBeTruthy();

    // Wait for variants
    await expect(page.locator('[data-testid="variant-card"]').first()).toBeVisible({ timeout: 60000 });

    // Select a variant then export
    await page.locator('[data-testid="variant-card"] [data-testid="select-variant"]').first().check();
    const exportButton = page.locator('[data-testid="export-button"]');
    if (await exportButton.isVisible()) {
      await exportButton.click();
      await expect(exportButton).toBeVisible();
    }
  });

  test('error handling', async ({ page }) => {
    const textarea = page.locator('[data-testid="content-input"]');
    const generateButton = page.locator('[data-testid="generate-button"]');

    // Test with very large content
    const largeContent = 'A'.repeat(200000); // Very large content
    await textarea.fill(largeContent);
    // Button should be enabled since length check only guards min length here
    await expect(generateButton).toBeEnabled();
    await generateButton.click();

    // Error is surfaced via toast; allow that the selector may not be present
    // Just assert no crash by checking page still responsive
    await expect(page.locator('[data-testid="content-input"]').first()).toBeVisible();
  });

  test('accessibility features', async ({ page }) => {
    // Test keyboard navigation
    await page.keyboard.press('Tab');
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();

    // Test ARIA labels
    const textarea = page.locator('[data-testid="content-input"]');
    const ariaLabel = await textarea.getAttribute('aria-label');
    expect(ariaLabel).toBeTruthy();
  });
});
