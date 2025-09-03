// Lightweight Sentry stub - safe no-op when no DSN provided
let Sentry = null;

// Lazy load Sentry only when needed
async function loadSentry() {
  if (!Sentry && import.meta.env.VITE_SENTRY_DSN) {
    try {
      Sentry = await import("@sentry/react");
      return Sentry;
    } catch (error) {
      console.warn("Failed to load Sentry:", error);
      return null;
    }
  }
  return Sentry;
}

// Initialize Sentry
export function initSentry() {
  const sentryDsn = import.meta.env.VITE_SENTRY_DSN;
  const environment = import.meta.env.VITE_ENVIRONMENT || "development";

  if (sentryDsn) {
    loadSentry().then(sentry => {
      if (sentry) {
        sentry.init({
          dsn: sentryDsn,
          environment: environment,
          integrations: [
            sentry.browserTracingIntegration(),
            sentry.replayIntegration({
              maskAllText: false,
              blockAllMedia: false,
            }),
          ],
          tracesSampleRate: environment === "production" ? 0.1 : 1.0,
          replaysSessionSampleRate: 0.1,
          replaysOnErrorSampleRate: 1.0,
        });
        console.log("Sentry initialized for environment:", environment);
      }
    });
  } else {
    console.log("Sentry DSN not provided, skipping initialization");
  }
}

// Capture exceptions
export function captureException(error, context = {}) {
  if (import.meta.env.VITE_SENTRY_DSN && Sentry) {
    Sentry.captureException(error, {
      tags: {
        component: "frontend",
        ...context.tags,
      },
      extra: {
        ...context,
      },
    });
  } else {
    console.error("Error (Sentry not configured):", error, context);
  }
}

// Capture messages
export function captureMessage(message, level = "info", context = {}) {
  if (import.meta.env.VITE_SENTRY_DSN && Sentry) {
    Sentry.captureMessage(message, level, {
      tags: {
        component: "frontend",
        ...context.tags,
      },
      extra: {
        ...context,
      },
    });
  } else {
    console.log(`Message (Sentry not configured): ${message}`, context);
  }
}

// Set user context
export function setUserContext(user) {
  if (import.meta.env.VITE_SENTRY_DSN && Sentry) {
    Sentry.setUser(user);
  }
}

// Add breadcrumb
export function addBreadcrumb(
  message,
  category = "user",
  level = "info",
  data = {}
) {
  if (import.meta.env.VITE_SENTRY_DSN && Sentry) {
    Sentry.addBreadcrumb({
      message,
      category,
      level,
      data,
    });
  }
}
