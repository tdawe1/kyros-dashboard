import * as Sentry from '@sentry/react'

// Initialize Sentry
export function initSentry() {
  const sentryDsn = import.meta.env.VITE_SENTRY_DSN
  const environment = import.meta.env.VITE_ENVIRONMENT || 'development'

  if (sentryDsn) {
    Sentry.init({
      dsn: sentryDsn,
      environment: environment,
      integrations: [
        Sentry.browserTracingIntegration(),
        Sentry.replayIntegration({
          maskAllText: false,
          blockAllMedia: false,
        }),
      ],
      // Performance Monitoring
      tracesSampleRate: environment === 'production' ? 0.1 : 1.0,
      // Session Replay
      replaysSessionSampleRate: 0.1,
      replaysOnErrorSampleRate: 1.0,
    })

    console.log('Sentry initialized for environment:', environment)
  } else {
    console.log('Sentry DSN not provided, skipping initialization')
  }
}

// Capture exceptions
export function captureException(error, context = {}) {
  if (import.meta.env.VITE_SENTRY_DSN) {
    Sentry.captureException(error, {
      tags: {
        component: 'frontend',
        ...context.tags,
      },
      extra: {
        ...context,
      },
    })
  } else {
    console.error('Error (Sentry not configured):', error, context)
  }
}

// Capture messages
export function captureMessage(message, level = 'info', context = {}) {
  if (import.meta.env.VITE_SENTRY_DSN) {
    Sentry.captureMessage(message, level, {
      tags: {
        component: 'frontend',
        ...context.tags,
      },
      extra: {
        ...context,
      },
    })
  } else {
    console.log(`Message (Sentry not configured): ${message}`, context)
  }
}

// Set user context
export function setUserContext(user) {
  if (import.meta.env.VITE_SENTRY_DSN) {
    Sentry.setUser(user)
  }
}

// Add breadcrumb
export function addBreadcrumb(message, category = 'user', level = 'info', data = {}) {
  if (import.meta.env.VITE_SENTRY_DSN) {
    Sentry.addBreadcrumb({
      message,
      category,
      level,
      data,
    })
  }
}
