import axios from "axios";

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor for auth tokens
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling and token refresh
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Attempt to refresh token
        const refreshToken = localStorage.getItem("refresh_token");
        if (refreshToken) {
          const response = await axios.post(
            `${api.defaults.baseURL}/auth/refresh`,
            {
              refresh_token: refreshToken,
            }
          );

          const { access_token } = response.data;
          localStorage.setItem("auth_token", access_token);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem("auth_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

// API functions
export const getKPIs = async () => {
  const response = await api.get("/api/kpis");
  return response.data;
};

export const getJobs = async () => {
  const response = await api.get("/api/jobs");
  return response.data;
};

export const getJob = async id => {
  const response = await api.get(`/api/jobs/${id}`);
  return response.data;
};

export const getPresets = async () => {
  const response = await api.get("/api/presets");
  return response.data;
};

export const createPreset = async preset => {
  const response = await api.post("/api/presets", preset);
  return response.data;
};

export const updatePreset = async (id, preset) => {
  const response = await api.put(`/api/presets/${id}`, preset);
  return response.data;
};

export const deletePreset = async id => {
  const response = await api.delete(`/api/presets/${id}`);
  return response.data;
};

export const generateContent = async request => {
  const response = await api.post("/api/generate", request);
  return response.data;
};

export const exportContent = async (content, format = "json") => {
  const response = await api.post("/api/export", { content, format });
  return response.data;
};

// Scheduler API functions
export const getScheduledJobs = async () => {
  const response = await api.get("/api/scheduler");
  return response.data;
};

export const createScheduledJob = async job => {
  const response = await api.post("/api/scheduler", job);
  return response.data;
};

export const updateScheduledJob = async (id, job) => {
  const response = await api.patch(`/api/scheduler/${id}`, job);
  return response.data;
};

export const deleteScheduledJob = async id => {
  const response = await api.delete(`/api/scheduler/${id}`);
  return response.data;
};

export const runScheduledJob = async id => {
  const response = await api.post(`/api/scheduler/${id}/run-now`);
  return response.data;
};

export const getScheduledJobRuns = async id => {
  const response = await api.get(`/api/scheduler/${id}/runs`);
  return response.data;
};

// Config API
export const getConfig = async () => {
  const response = await api.get("/api/config");
  return response.data;
};

// Export the axios instance as well
export { api };
