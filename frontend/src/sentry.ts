export async function initSentry() {
  const dsn = import.meta.env.VITE_SENTRY_DSN;
  if (!dsn) return;
  const Sentry = await import("@sentry/react");
  Sentry.init({ dsn, tracesSampleRate: 1.0, replaysSessionSampleRate: 0.1 });
}
