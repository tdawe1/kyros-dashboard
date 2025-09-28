import { defineConfig } from '@playwright/test';

const PORT = process.env.PORT ?? '3001';

export default defineConfig({
  use: { baseURL: process.env.PLAYWRIGHT_BASE_URL ?? `http://localhost:${PORT}` },
  webServer: {
    command: 'npm run preview -- --strictPort --host --port ' + PORT,
    url: `http://localhost:${PORT}`,
    reuseExistingServer: !process.env.CI,
    timeout: 120000
  },
});
