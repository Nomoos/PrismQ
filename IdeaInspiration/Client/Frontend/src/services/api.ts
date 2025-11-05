import axios, { AxiosError } from 'axios'
import { useNotificationStore } from '@/stores/notifications'

/**
 * Axios instance configured for PrismQ API
 */
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000, // 30 second timeout to prevent infinite loading
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * API response interceptor for error handling
 */
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Get notification store (safe to call here as it's not during setup)
    const notifications = useNotificationStore()

    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      // Request timeout
      notifications.error({
        title: 'Request Timeout',
        message: 'The request took too long to complete. Please try again.',
      })
    } else if (error.response) {
      // Server responded with error
      const data = error.response.data as any
      const message = data.detail || 'An error occurred'
      const errorCode = data.error_code

      notifications.error({
        title: `Error ${error.response.status}`,
        message,
        errorCode,
      })
    } else if (error.request) {
      // Request made but no response
      notifications.error({
        title: 'Connection Error',
        message: 'Cannot connect to server. Is it running?',
      })
    } else {
      // Something else happened
      notifications.error({
        title: 'Error',
        message: error.message,
      })
    }

    return Promise.reject(error)
  }
)

export default api
