import api from './api'

export interface HealthCheckResponse {
  status: string
  timestamp: number
  database: string
}

export const healthService = {
  /**
   * Check API and database health
   * This endpoint does not require authentication
   */
  async check(): Promise<HealthCheckResponse> {
    return api.get<HealthCheckResponse>('/health')
  }
}

export default healthService
