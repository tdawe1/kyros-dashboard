import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Health check
export const healthCheck = async () => {
  const response = await api.get('/api/health')
  return response.data
}

// KPIs
export const getKPIs = async () => {
  const response = await api.get('/api/kpis')
  return response.data
}

// Jobs
export const getJobs = async () => {
  const response = await api.get('/api/jobs')
  return response.data
}

export const getJob = async (jobId) => {
  const response = await api.get(`/api/jobs/${jobId}`)
  return response.data
}

// Generate content
export const generateContent = async (data) => {
  const response = await api.post('/api/generate', data)
  return response.data
}

// Export content
export const exportContent = async (data) => {
  const response = await api.post('/api/export', data)
  return response.data
}

// Presets
export const getPresets = async () => {
  const response = await api.get('/api/presets')
  return response.data
}

export const createPreset = async (data) => {
  const response = await api.post('/api/presets', data)
  return response.data
}

export const updatePreset = async (presetId, data) => {
  const response = await api.put(`/api/presets/${presetId}`, data)
  return response.data
}

export const deletePreset = async (presetId) => {
  const response = await api.delete(`/api/presets/${presetId}`)
  return response.data
}

export default api
