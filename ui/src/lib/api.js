import axios from 'axios'
import { API_CONFIG } from '../constants'

const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const { response } = error
    
    if (response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    
    // Transform error for consistent handling
    const errorMessage = response?.data?.detail || 
                        response?.data?.message || 
                        error.message || 
                        'An unexpected error occurred'
    
    return Promise.reject({
      message: errorMessage,
      status: response?.status,
      data: response?.data
    })
  }
)

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
