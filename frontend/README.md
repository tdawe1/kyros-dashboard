# Kyros Dashboard Frontend

A modern React application for content repurposing and AI-powered content generation.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend API running on port 8000

### Development Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Application will be available at http://localhost:3001
```

## 🏗️ Architecture

### Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **TanStack Query** - Data fetching and caching
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Playwright** - E2E testing

### Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   ├── contexts/           # React contexts (Theme, etc.)
│   ├── hooks/              # Custom React hooks
│   ├── layouts/            # Layout components
│   ├── pages/              # Page components
│   ├── tools/              # Tool-specific components
│   ├── ui/                 # UI components
│   └── utils/              # Utility functions
├── e2e/                    # E2E tests
├── dist/                   # Build output
└── public/                 # Static assets
```

## 🎯 Key Features

### Content Generation Studio
- Multi-channel content repurposing (LinkedIn, Twitter, Newsletter, Blog)
- Tone and style customization
- Real-time content generation
- Variant management and editing

### Job Monitoring
- Real-time job status tracking
- Job history and analytics
- Export functionality

### Settings & Configuration
- Preset management
- API configuration
- Export settings

### Responsive Design
- Mobile-first approach
- Dark/light theme support
- Accessible navigation

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### E2E Tests
```bash
# Install Playwright
npx playwright install

# Run E2E tests
npx playwright test

# Run with UI
npx playwright test --ui
```

For detailed E2E testing information, see [E2E Testing Guide](../docs/E2E_TESTING.md).

### Test Coverage

The application uses comprehensive testing strategies:

- **Unit Tests**: Component logic and hooks
- **E2E Tests**: Complete user workflows
- **Accessibility Tests**: Screen reader compatibility
- **Cross-browser Tests**: Chrome, Firefox, Safari, Mobile

## 🎨 UI Components

### Core Components

- **VariantCard** - Displays generated content variants
- **VariantsGallery** - Grid/list view of variants
- **JobTable** - Job monitoring and management
- **Sidebar** - Navigation and tool access
- **ThemeToggle** - Dark/light mode switching

### Data Test IDs

All interactive elements use `data-testid` attributes for reliable testing:

```jsx
// Example usage
<button data-testid="generate-button">Generate</button>
<input data-testid="content-input" />
<div data-testid="variant-card">...</div>
```

## 🔧 Development

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run test         # Run unit tests
npm run test:e2e     # Run E2E tests
npm run lint         # Run ESLint
```

### Environment Variables

Create a `.env.local` file for local development:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=Kyros Dashboard
```

### Code Style

- **ESLint** - Code linting
- **Prettier** - Code formatting
- **TypeScript** - Type safety (optional)

## 🚀 Deployment

### Build Process

```bash
# Build for production
npm run build

# Output will be in dist/ directory
```

### Deployment Options

- **Static Hosting**: Vercel, Netlify, GitHub Pages
- **Docker**: Containerized deployment
- **CDN**: Global content delivery

## 🔌 API Integration

### Backend Communication

The frontend communicates with the backend API:

- **Base URL**: `http://localhost:8000` (development)
- **Endpoints**: `/api/generate`, `/api/jobs`, `/api/health`
- **Authentication**: Token-based (when enabled)

### Data Flow

1. **User Input** → Form validation
2. **API Request** → Backend processing
3. **Response** → State management
4. **UI Update** → Real-time feedback

## 🎯 Performance

### Optimization Strategies

- **Code Splitting** - Lazy loading of routes
- **Bundle Analysis** - Optimized bundle size
- **Caching** - TanStack Query for API caching
- **Image Optimization** - Responsive images

### Monitoring

- **Performance Metrics** - Core Web Vitals
- **Error Tracking** - Error boundaries
- **Analytics** - User interaction tracking

## 🔒 Security

### Best Practices

- **Input Validation** - Client-side validation
- **XSS Prevention** - Sanitized user input
- **CSRF Protection** - Token-based requests
- **Content Security Policy** - Restricted resource loading

## 📱 Responsive Design

### Breakpoints

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Mobile Features

- **Touch Navigation** - Swipe gestures
- **Mobile Menu** - Collapsible navigation
- **Responsive Tables** - Horizontal scrolling
- **Touch Targets** - Minimum 44px touch areas

## 🌙 Theme Support

### Dark/Light Mode

- **System Preference** - Automatic detection
- **Manual Toggle** - User preference
- **Persistence** - Local storage
- **Smooth Transitions** - CSS transitions

## ♿ Accessibility

### WCAG Compliance

- **Keyboard Navigation** - Full keyboard support
- **Screen Reader** - ARIA labels and roles
- **Color Contrast** - WCAG AA compliance
- **Focus Management** - Visible focus indicators

## 🔄 State Management

### Data Flow

- **TanStack Query** - Server state
- **React Context** - Global UI state
- **Local State** - Component state
- **URL State** - Route parameters

## 🛠️ Troubleshooting

### Common Issues

1. **Port Conflicts**:
   ```bash
   # Use different port
   npm run dev -- --port 3002
   ```

2. **API Connection**:
   - Verify backend is running on port 8000
   - Check CORS configuration
   - Verify API endpoints

3. **Build Failures**:
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

### Debug Tools

- **React DevTools** - Component inspection
- **TanStack Query DevTools** - Query debugging
- **Playwright Inspector** - E2E test debugging

## 📚 Resources

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [TanStack Query](https://tanstack.com/query)
- [Tailwind CSS](https://tailwindcss.com/)
- [Playwright Testing](https://playwright.dev/)

## 🤝 Contributing

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch
3. **Write** tests for new features
4. **Submit** a pull request

### Code Standards

- **ESLint** rules must pass
- **Tests** must be included
- **Documentation** must be updated
- **Accessibility** must be maintained

## 📄 License

This project is licensed under the MIT License.
