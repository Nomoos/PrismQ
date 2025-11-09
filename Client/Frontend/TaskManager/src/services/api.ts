import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig, type CancelTokenSource } from 'axios'
import { APIError, NetworkError } from '../types'

class ApiClient {
  private client: AxiosInstance
  private maxRetries = 3
  private retryDelay = 1000
  private pendingRequests = new Map<string, CancelTokenSource>()

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': import.meta.env.VITE_API_KEY || ''
      }
    })

    // Request interceptor for logging and deduplication
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        if (import.meta.env.DEV) {
          console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data)
        }
        
        // Generate request key for deduplication
        const requestKey = this.getRequestKey(config)
        
        // Cancel duplicate requests (only for GET requests to avoid side effects)
        if (config.method === 'get' && this.pendingRequests.has(requestKey)) {
          const source = this.pendingRequests.get(requestKey)
          source?.cancel('Duplicate request cancelled')
        }
        
        // Store cancel token for this request
        const cancelSource = axios.CancelToken.source()
        config.cancelToken = cancelSource.token
        if (config.method === 'get') {
          this.pendingRequests.set(requestKey, cancelSource)
        }
        
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor for error handling and cleanup
    this.client.interceptors.response.use(
      (response) => {
        // Cleanup completed request from pending map
        const requestKey = this.getRequestKey(response.config)
        this.pendingRequests.delete(requestKey)
        return response
      },
      async (error: AxiosError) => {
        // Cleanup failed request from pending map
        if (error.config) {
          const requestKey = this.getRequestKey(error.config)
          this.pendingRequests.delete(requestKey)
        }
        
        // Don't retry if request was cancelled
        if (axios.isCancel(error)) {
          return Promise.reject(error)
        }
        
        const config = error.config as InternalAxiosRequestConfig & { _retry?: number }
        
        // Handle network errors with retry
        if (!error.response && config && (!config._retry || config._retry < this.maxRetries)) {
          config._retry = (config._retry || 0) + 1
          console.log(`[API] Retrying request (${config._retry}/${this.maxRetries})...`)
          
          await new Promise(resolve => setTimeout(resolve, this.retryDelay * config._retry!))
          return this.client.request(config)
        }
        
        // Transform error
        if (error.response) {
          // Server responded with error
          const message = (error.response.data as any)?.message || 
                         (error.response.data as any)?.error || 
                         'API Error'
          throw new APIError(message, error.response.status, error.response.data)
        } else if (error.request) {
          // Network error
          throw new NetworkError('Network error - please check your connection')
        } else {
          throw new Error(error.message)
        }
      }
    )
  }

  /**
   * Generate a unique key for request deduplication
   */
  private getRequestKey(config: InternalAxiosRequestConfig): string {
    const { method, url, params, data } = config
    return `${method}:${url}:${JSON.stringify(params)}:${JSON.stringify(data)}`
  }

  /**
   * Cancel all pending requests
   */
  cancelAllRequests(message = 'Requests cancelled'): void {
    this.pendingRequests.forEach((source) => {
      source.cancel(message)
    })
    this.pendingRequests.clear()
  }

  /**
   * Cancel specific request by key pattern
   */
  cancelRequests(pattern: string, message = 'Request cancelled'): void {
    this.pendingRequests.forEach((source, key) => {
      if (key.includes(pattern)) {
        source.cancel(message)
        this.pendingRequests.delete(key)
      }
    })
  }

  async get<T>(url: string, params?: Record<string, any>): Promise<T> {
    const response = await this.client.get<T>(url, { params })
    return response.data
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post<T>(url, data)
    return response.data
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.put<T>(url, data)
    return response.data
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<T>(url)
    return response.data
  }
}

export const api = new ApiClient()
export default api
