# E2E Testing Guide

This guide covers the End-to-End (E2E) testing setup and execution for the Kyros Dashboard frontend application.

## 🧪 Overview

The E2E tests use Playwright to test the complete user journey through the application, ensuring that all features work correctly from the user's perspective.

## 📁 Test Structure

### Test Files

- **`frontend/e2e/full-flow.spec.js`** - Complete content generation workflow
- **`frontend/e2e/navigation.spec.js`** - Navigation and routing tests
- **`frontend/e2e/studio.spec.js`** - Studio page specific functionality

### Test Configuration

- **`frontend/playwright.config.js`** - Playwright configuration
- **Base URL**: `http://localhost:3001` (configurable via `PLAYWRIGHT_BASE_URL`)
- **Browsers**: Chromium, Firefox, WebKit, Mobile Chrome, Mobile Safari

## 🎯 Test Coverage

### Full Flow Tests (`full-flow.spec.js`)

Tests the complete content generation workflow:

1. **Navigation to Studio**
   - Clicks "Studio" navigation link
   - Verifies URL change to `/studio`

2. **Content Input**
   - Uses `[data-testid="content-input"]` to locate textarea
   - Fills with sample article content
   - Validates character count display

3. **Channel Selection**
   - Uses `[data-testid="channel-linkedin"]` and `[data-testid="channel-twitter"]`
   - Clicks channel buttons to select multiple channels

4. **Tone Selection**
   - Uses `[data-testid="tone-professional"]` for tone selection
   - Verifies tone selection works

5. **Content Generation**
   - Uses `[data-testid="generate-button"]` to trigger generation
   - Waits for loading state
   - Verifies variants appear using `[data-testid="variant-card"]`

6. **Variant Interaction**
   - Uses `[data-testid="accept-button"]` to accept variants
   - Tests variant selection and interaction

7. **Export Functionality**
   - Uses `[data-testid="export-button"]` for bulk export
   - Verifies export options and download

### Navigation Tests (`navigation.spec.js`)

Tests application navigation and routing:

1. **Page Navigation**
   - Tests navigation between Dashboard, Studio, Jobs, Settings
   - Verifies URL changes and page titles using `[data-testid="page-title"]`

2. **Sidebar Navigation**
   - Uses `[data-testid="sidebar"]` to locate navigation
   - Tests all navigation links

3. **Theme Toggle**
   - Uses `[data-testid="theme-toggle"]` to test dark/light mode
   - Verifies theme persistence

4. **Mobile Navigation**
   - Uses `[data-testid="mobile-menu"]` for mobile menu testing
   - Tests responsive navigation

5. **Page Loading States**
   - Verifies all pages load without errors
   - Uses `[data-testid="main-content"]` to check main content visibility

### Studio Page Tests (`studio.spec.js`)

Tests Studio page specific functionality:

1. **Page Load**
   - Verifies page title using `[data-testid="page-title"]`
   - Checks content input using `[data-testid="content-input"]`
   - Verifies channel selection using `[data-testid="channel-linkedin"]`
   - Checks generate button using `[data-testid="generate-button"]`

2. **Input Validation**
   - Tests empty input validation
   - Tests minimum length validation
   - Tests maximum length validation

3. **Channel Selection**
   - Tests all channel buttons: `[data-testid="channel-{channel}"]`
   - Verifies channel selection state

4. **Tone Selection**
   - Tests tone buttons: `[data-testid="tone-{tone}"]`
   - Verifies tone selection works

5. **Content Generation**
   - Tests complete generation workflow
   - Verifies loading states
   - Checks variant appearance

6. **Variant Interaction**
   - Uses `[data-testid="edit-button"]` for editing
   - Uses `[data-testid="copy-button"]` for copying
   - Tests variant actions

7. **Export Functionality**
   - Uses `[data-testid="export-button"]` for export
   - Tests export options and download

8. **Error Handling**
   - Tests large content handling
   - Tests network error simulation

9. **Accessibility**
   - Tests keyboard navigation
   - Verifies ARIA labels
   - Tests screen reader compatibility

## 🔧 Data Test IDs

The application uses consistent `data-testid` attributes for reliable E2E testing:

### Page Elements
- `[data-testid="page-title"]` - Page titles
- `[data-testid="main-content"]` - Main content area
- `[data-testid="sidebar"]` - Navigation sidebar

### Studio Page
- `[data-testid="content-input"]` - Content textarea
- `[data-testid="channel-{channel}"]` - Channel selection buttons
- `[data-testid="tone-{tone}"]` - Tone selection buttons
- `[data-testid="generate-button"]` - Generate content button

### Variant Cards
- `[data-testid="variant-card"]` - Individual variant cards
- `[data-testid="accept-button"]` - Accept variant button
- `[data-testid="edit-button"]` - Edit variant button
- `[data-testid="copy-button"]` - Copy variant button
- `[data-testid="download-button"]` - Download variant button

### Navigation
- `[data-testid="mobile-menu"]` - Mobile menu button
- `[data-testid="theme-toggle"]` - Theme toggle button

### Tables and Lists
- `[data-testid="jobs-table"]` - Jobs table

### Modals
- `[data-testid="edit-modal"]` - Edit modal textarea

## 🚀 Running Tests

### Prerequisites

1. **Start the application**:
   ```bash
   # Backend (port 8000)
   cd backend
   poetry run uvicorn main:app --reload --port 8000

   # Frontend (port 3001)
   cd frontend
   npm run dev
   ```

2. **Install Playwright**:
   ```bash
   cd frontend
   npm install
   npx playwright install
   ```

### Running Tests

```bash
# Run all E2E tests
cd frontend
npx playwright test

# Run specific test file
npx playwright test e2e/full-flow.spec.js

# Run tests in headed mode (see browser)
npx playwright test --headed

# Run tests in debug mode
npx playwright test --debug

# Run tests on specific browser
npx playwright test --project=chromium
```

### Test Reports

```bash
# Generate HTML report
npx playwright show-report

# Generate JSON report
npx playwright test --reporter=json
```

## 🔍 Debugging Tests

### Common Issues

1. **Element not found**:
   - Check if `data-testid` attributes are present
   - Verify element is visible and not hidden
   - Check for timing issues (add waits)

2. **Navigation failures**:
   - Verify routes are properly configured
   - Check for authentication requirements
   - Ensure backend is running

3. **Content generation failures**:
   - Check backend API endpoints
   - Verify mock data is available
   - Check for rate limiting

### Debug Commands

```bash
# Run single test with debug
npx playwright test --debug e2e/full-flow.spec.js

# Run with trace
npx playwright test --trace=on

# Run with video recording
npx playwright test --video=on
```

## 📊 Test Data

### Sample Content

The tests use predefined sample content for consistent testing:

```javascript
const sampleArticle = `
  Artificial intelligence is revolutionizing the way businesses operate in the modern world.
  From machine learning algorithms that power recommendation systems to natural language
  processing that enables chatbots, AI is becoming increasingly integrated into our daily lives.

  Companies are leveraging AI to improve efficiency, reduce costs, and enhance customer
  experiences. However, with these benefits come challenges around ethics, privacy, and
  the future of work.
`;
```

### Test Channels

- LinkedIn (`linkedin`)
- Twitter (`twitter`)
- Newsletter (`newsletter`)
- Blog (`blog`)

### Test Tones

- Professional (`professional`)
- Casual (`casual`)
- Engaging (`engaging`)
- Formal (`formal`)

## 🎯 Best Practices

### Selector Strategy

1. **Use data-testid attributes** for reliable element selection
2. **Avoid CSS selectors** that may change with styling updates
3. **Use semantic selectors** when data-testid is not available
4. **Prefer text content** for user-facing elements

### Test Organization

1. **Group related tests** in describe blocks
2. **Use descriptive test names** that explain the scenario
3. **Keep tests independent** - each test should be able to run alone
4. **Use beforeEach** for common setup

### Assertions

1. **Use specific assertions** - prefer `toBeVisible()` over `toBeInTheDocument()`
2. **Add appropriate timeouts** for async operations
3. **Test both positive and negative cases**
4. **Verify user feedback** (toasts, error messages, etc.)

## 🔄 Continuous Integration

The E2E tests are configured to run in CI/CD pipelines:

- **GitHub Actions**: Runs on pull requests and main branch
- **Parallel execution**: Tests run in parallel for faster feedback
- **Artifact collection**: Screenshots and videos are saved on failure
- **Cross-browser testing**: Tests run on multiple browsers

## 📝 Maintenance

### Adding New Tests

1. **Identify the user journey** to test
2. **Add appropriate data-testid attributes** to components
3. **Write test cases** following existing patterns
4. **Update documentation** with new test coverage

### Updating Existing Tests

1. **Check for breaking changes** in component structure
2. **Update selectors** if data-testid attributes change
3. **Verify test data** is still relevant
4. **Update documentation** to reflect changes

## 🚨 Troubleshooting

### Common Failures

1. **Timeout errors**: Increase timeout or add explicit waits
2. **Element not found**: Check selector and element visibility
3. **Navigation errors**: Verify routing configuration
4. **API errors**: Check backend status and endpoints

### Debug Tools

- **Playwright Inspector**: Interactive debugging
- **Trace Viewer**: Step-by-step test execution
- **Screenshots**: Visual debugging on failures
- **Console logs**: JavaScript error debugging

## 📚 Resources

- [Playwright Documentation](https://playwright.dev/)
- [Testing Best Practices](https://playwright.dev/docs/best-practices)
- [Selector Strategies](https://playwright.dev/docs/selectors)
- [Debugging Guide](https://playwright.dev/docs/debug)
