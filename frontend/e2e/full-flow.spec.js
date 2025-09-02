// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Kyros Dashboard - Full Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the dashboard
    await page.goto('/');

    // Wait for the page to load
    await expect(page.locator('h1')).toBeVisible();
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

    const textarea = page.locator('textarea[placeholder*="article"], textarea[placeholder*="content"], textarea[placeholder*="text"]').first();
    await textarea.fill(sampleArticle);

    // Step 3: Select channels
    await page.check('input[type="checkbox"][value="linkedin"]');
    await page.check('input[type="checkbox"][value="twitter"]');

    // Step 4: Set tone
    const toneSelect = page.locator('select[name="tone"], select[data-testid="tone-select"]').first();
    if (await toneSelect.isVisible()) {
      await toneSelect.selectOption('professional');
    }

    // Step 5: Generate content
    const generateButton = page.locator('button:has-text("Generate"), button:has-text("Create"), button[type="submit"]').first();
    await generateButton.click();

    // Step 6: Wait for variants to appear
    await expect(page.locator('[data-testid="variant-card"], .variant-card, [class*="variant"]').first()).toBeVisible({ timeout: 30000 });

    // Step 7: Verify variants are displayed
    const variantCards = page.locator('[data-testid="variant-card"], .variant-card, [class*="variant"]');
    const variantCount = await variantCards.count();
    expect(variantCount).toBeGreaterThan(0);

    // Step 8: Select a variant (click accept or select button)
    const firstVariant = variantCards.first();
    const acceptButton = firstVariant.locator('button:has-text("Accept"), button:has-text("Select"), button:has-text("Use")').first();

    if (await acceptButton.isVisible()) {
      await acceptButton.click();
    } else {
      // If no accept button, just click on the variant card
      await firstVariant.click();
    }

    // Step 9: Export functionality
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first();
    if (await exportButton.isVisible()) {
      await exportButton.click();

      // Verify export options or download
      await expect(page.locator('text=CSV, text=JSON, text=Download, [data-testid="export-format"]').first()).toBeVisible();
    }

    // Step 10: Verify the flow completed successfully
    await expect(page.locator('text=Success, text=Completed, text=Generated').first()).toBeVisible({ timeout: 10000 });
  });

  test('content generation with different channels', async ({ page }) => {
    await page.click('text=Studio');

    const sampleText = 'This is a test article about the latest trends in technology and innovation.';
    const textarea = page.locator('textarea').first();
    await textarea.fill(sampleText);

    // Test different channel combinations
    const channels = ['linkedin', 'twitter', 'newsletter', 'blog'];

    for (const channel of channels) {
      // Clear previous selections
      // Uncheck specific checkboxes by targeting the channel selection area
      const channelCheckboxes = page.locator('[data-testid="channel-select"] input[type="checkbox"], .channel-selection input[type="checkbox"]');
      const checkboxCount = await channelCheckboxes.count();
      for (let i = 0; i < checkboxCount; i++) {
        const checkbox = channelCheckboxes.nth(i);
        if (await checkbox.isChecked()) {
          await checkbox.uncheck();
        }
      }

      // Select current channel
      await page.check(`input[type="checkbox"][value="${channel}"]`);

      // Generate content
      await page.click('button:has-text("Generate"), button:has-text("Create")');

      // Wait for variants
      await expect(page.locator('[data-testid="variant-card"], .variant-card').first()).toBeVisible({ timeout: 15000 });

      // Verify channel-specific content
      const variantText = await page.locator('[data-testid="variant-card"], .variant-card').first().textContent();
      expect(variantText).toBeTruthy();
    }
  });

  test('error handling for invalid input', async ({ page }) => {
    await page.click('text=Studio');

    // Test with empty input
    const generateButton = page.locator('button:has-text("Generate"), button:has-text("Create")').first();
    await generateButton.click();

    // Should show error message
    await expect(page.locator('text=required, text=minimum, text=error').first()).toBeVisible({ timeout: 5000 });

    // Test with very short input
    const textarea = page.locator('textarea').first();
    await textarea.fill('Short');
    await generateButton.click();

    // Should show validation error
    await expect(page.locator('text=too short, text=minimum length, text=100 characters').first()).toBeVisible({ timeout: 5000 });
  });

  test('responsive design on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto('/');

    // Check that mobile navigation works
    const mobileMenuButton = page.locator('button[aria-label*="menu"], button:has-text("Menu"), [data-testid="mobile-menu"]').first();
    if (await mobileMenuButton.isVisible()) {
      await mobileMenuButton.click();
    }

    // Navigate to Studio
    await page.click('text=Studio');

    // Verify mobile layout
    await expect(page.locator('textarea').first()).toBeVisible();
    await expect(page.locator('button:has-text("Generate")').first()).toBeVisible();
  });
});
