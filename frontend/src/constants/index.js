// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
};

// Sentry Configuration
export const SENTRY_CONFIG = {
  DSN: import.meta.env.VITE_SENTRY_DSN,
  ENVIRONMENT: import.meta.env.VITE_ENVIRONMENT || "development",
  RELEASE: import.meta.env.VITE_RELEASE_VERSION || "1.0.0",
};

// Content Generation
export const CHANNELS = [
  { id: "linkedin", name: "LinkedIn", icon: "💼", maxLength: 3000 },
  { id: "twitter", name: "Twitter", icon: "🐦", maxLength: 280 },
  { id: "newsletter", name: "Newsletter", icon: "📧", maxLength: 5000 },
  { id: "blog", name: "Blog", icon: "📝", maxLength: 10000 },
];

export const TONES = [
  { id: "professional", name: "Professional" },
  { id: "casual", name: "Casual" },
  { id: "technical", name: "Technical" },
  { id: "creative", name: "Creative" },
];

export const PRESETS = [
  { id: "default", name: "Default" },
  { id: "marketing", name: "Marketing" },
  { id: "technical", name: "Technical" },
  { id: "newsletter", name: "Newsletter" },
];

// Job Status
export const JOB_STATUS = {
  PENDING: "pending",
  PROCESSING: "processing",
  COMPLETED: "completed",
  FAILED: "failed",
};

export const JOB_STATUS_COLORS = {
  [JOB_STATUS.PENDING]: "bg-yellow-500",
  [JOB_STATUS.PROCESSING]: "bg-blue-500",
  [JOB_STATUS.COMPLETED]: "bg-green-500",
  [JOB_STATUS.FAILED]: "bg-red-500",
};

export const JOB_STATUS_LABELS = {
  [JOB_STATUS.PENDING]: "Pending",
  [JOB_STATUS.PROCESSING]: "Processing",
  [JOB_STATUS.COMPLETED]: "Completed",
  [JOB_STATUS.FAILED]: "Failed",
};

// Validation
export const VALIDATION_RULES = {
  MIN_INPUT_LENGTH: 100,
  MAX_INPUT_LENGTH: 50000,
  MIN_PRESET_NAME_LENGTH: 2,
  MAX_PRESET_NAME_LENGTH: 50,
};

// UI Configuration
export const UI_CONFIG = {
  SIDEBAR_WIDTH: 256, // 64 * 4 (w-64)
  TOAST_DURATION: 5000,
  DEBOUNCE_DELAY: 300,
};
