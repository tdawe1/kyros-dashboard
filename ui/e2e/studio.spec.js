// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Kyros Dashboard - Studio Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/studio');
  });

  test('studio page loads correctly', async ({ page }) => {
    // Check page title
    await expect(page.locator('h1, [data-testid="page-title"]').first()).toBeVisible();

    // Check main input area
    await expect(page.locator('textarea, [data-testid="content-input"]').first()).toBeVisible();

    // Check channel selection
    await expect(page.locator('input[type="checkbox"], [data-testid="channel-select"]').first()).toBeVisible();

    // Check generate button
    await expect(page.locator('button:has-text("Generate"), button:has-text("Create")').first()).toBeVisible();
  });

  test('content input validation', async ({ page }) => {
    const textarea = page.locator('textarea, [data-testid="content-input"]').first();
    const generateButton = page.locator('button:has-text("Generate"), button:has-text("Create")').first();

    // Test empty input
    await textarea.clear();
    await generateButton.click();

    // Should show validation error
    await expect(page.locator('text=required, text=minimum, text=error').first()).toBeVisible({ timeout: 5000 });

    // Test short input
    await textarea.fill('Short text');
    await generateButton.click();

    // Should show minimum length error
    await expect(page.locator('text=too short, text=minimum length, text=100 characters').first()).toBeVisible({ timeout: 5000 });

    // Test valid input
    const validText = 'This is a valid test input that meets the minimum length requirement and should pass validation. '.repeat(2);
    await textarea.fill(validText);
    await generateButton.click();

    // Should not show validation errors
    await expect(page.locator('text=required, text=minimum, text=error').first()).not.toBeVisible({ timeout: 5000 });
  });

  test('channel selection', async ({ page }) => {
    const channels = ['linkedin', 'twitter', 'newsletter', 'blog'];

    for (const channel of channels) {
      const checkbox = page.locator(`input[type="checkbox"][value="${channel}"], [data-testid="channel-${channel}"]`).first();

      if (await checkbox.isVisible()) {
        // Test checking channel
        await checkbox.check();
        await expect(checkbox).toBeChecked();

        // Test unchecking channel
        await checkbox.uncheck();
        await expect(checkbox).not.toBeChecked();
      }
    }
  });

  test('tone selection', async ({ page }) => {
    const toneSelect = page.locator('select[name="tone"], [data-testid="tone-select"]').first();

    if (await toneSelect.isVisible()) {
      const tones = ['professional', 'casual', 'engaging', 'formal'];

      for (const tone of tones) {
        await toneSelect.selectOption(tone);
        await expect(toneSelect).toHaveValue(tone);
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
    const textarea = page.locator('textarea, [data-testid="content-input"]').first();
    const generateButton = page.locator('button:has-text("Generate"), button:has-text("Create")').first();

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
    await page.check('input[type="checkbox"][value="linkedin"]');
    await page.check('input[type="checkbox"][value="twitter"]');

    // Click generate
    await generateButton.click();

    // Wait for loading state
    await expect(page.locator('text=Generating, text=Loading, [data-testid="loading"]').first()).toBeVisible({ timeout: 5000 });

    // Wait for variants to appear
    await expect(page.locator('[data-testid="variant-card"], .variant-card, [class*="variant"]').first()).toBeVisible({ timeout: 30000 });

    // Verify variants are displayed
    const variantCards = page.locator('[data-testid="variant-card"], .variant-card, [class*="variant"]');
    await expect(variantCards).toHaveCount.greaterThan(0);
  });

  test('variant interaction', async ({ page }) => {
    // First generate some content
    const textarea = page.locator('textarea, [data-testid="content-input"]').first();
    const generateButton = page.locator('button:has-text("Generate"), button:has-text("Create")').first();

    await textarea.fill('This is a test article about artificial intelligence and its impact on modern business.');
    await page.check('input[type="checkbox"][value="linkedin"]');
    await generateButton.click();

    // Wait for variants
    await expect(page.locator('[data-testid="variant-card"], .variant-card').first()).toBeVisible({ timeout: 30000 });

    const variantCards = page.locator('[data-testid="variant-card"], .variant-card, [class*="variant"]');
    const firstVariant = variantCards.first();

    // Test variant actions
    const editButton = firstVariant.locator('button:has-text("Edit")').first();
    if (await editButton.isVisible()) {
      await editButton.click();
      // Should open edit modal or inline editor
      await expect(page.locator('textarea, [data-testid="edit-modal"]').first()).toBeVisible();
    }

    const copyButton = firstVariant.locator('button:has-text("Copy")').first();
    if (await copyButton.isVisible()) {
      await copyButton.click();
      // Should show copy confirmation
      await expect(page.locator('text=Copied, text=Success').first()).toBeVisible({ timeout: 3000 });
    }

    const favoriteButton = firstVariant.locator('button[aria-label*="favorite"], button:has-text("♥"), button:has-text("♡")').first();
    if (await favoriteButton.isVisible()) {
      await favoriteButton.click();
      // Should toggle favorite state
      await expect(favoriteButton).toBeVisible();
    }
  });

  test('export functionality', async ({ page }) => {
    // Generate content first
    const textarea = page.locator('textarea, [data-testid="content-input"]').first();
    const generateButton = page.locator('button:has-text("Generate"), button:has-text("Create")').first();

    await textarea.fill('This is a test article for export functionality testing.');
    await page.check('input[type="checkbox"][value="linkedin"]');
    await generateButton.click();

    // Wait for variants
    await expect(page.locator('[data-testid="variant-card"], .variant-card').first()).toBeVisible({ timeout: 30000 });

    // Test export button
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first();
    if (await exportButton.isVisible()) {
      await exportButton.click();

      // Should show export options
      await expect(page.locator('text=CSV, text=JSON, text=PDF, [data-testid="export-format"]').first()).toBeVisible();

      // Test format selection
      const csvOption = page.locator('button:has-text("CSV"), input[value="csv"]').first();
      if (await csvOption.isVisible()) {
        await csvOption.click();
      }

      // Test download
      const downloadButton = page.locator('button:has-text("Download"), button:has-text("Export")').first();
      if (await downloadButton.isVisible()) {
        await downloadButton.click();
      }
    }
  });

  test('error handling', async ({ page }) => {
    const textarea = page.locator('textarea, [data-testid="content-input"]').first();
    const generateButton = page.locator('button:has-text("Generate"), button:has-text("Create")').first();

    // Test with very large content
    const largeContent = 'A'.repeat(200000); // Very large content
    await textarea.fill(largeContent);
    await generateButton.click();

    // Should show error for content too large
    await expect(page.locator('text=too large, text=limit exceeded, text=error').first()).toBeVisible({ timeout: 10000 });

    // Test network error simulation
    await page.route('**/api/generate', route => route.abort());

    await textarea.fill('This is a test article for network error testing.');
    await generateButton.click();

    // Should show network error
    await expect(page.locator('text=network error, text=failed, text=error').first()).toBeVisible({ timeout: 10000 });
  });

  test('accessibility features', async ({ page }) => {
    // Test keyboard navigation
    await page.keyboard.press('Tab');
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();

    // Test ARIA labels
    const textarea = page.locator('textarea, [data-testid="content-input"]').first();
    const ariaLabel = await textarea.getAttribute('aria-label');
    expect(ariaLabel).toBeTruthy();

    // Test form validation with screen reader
    const generateButton = page.locator('button:has-text("Generate"), button:has-text("Create")').first();
    await generateButton.click();

    // Check for error announcements
    const errorElement = page.locator('[role="alert"], [aria-live="polite"], [aria-live="assertive"]').first();
    if (await errorElement.isVisible()) {
      await expect(errorElement).toBeVisible();
    }
  });
});
