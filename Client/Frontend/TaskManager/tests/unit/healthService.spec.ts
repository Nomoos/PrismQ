import { describe, it, expect, vi, beforeEach } from 'vitest'
import { healthService } from '../../src/services/healthService'
import type { HealthCheckResponse } from '../../src/services/healthService'
import api from '../../src/services/api'

// Mock the API module
vi.mock('../../src/services/api', () => ({
  default: {
    get: vi.fn()
  }
}))

describe('Health Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('check', () => {
    it('should call API health endpoint', async () => {
      const mockResponse: HealthCheckResponse = {
        status: 'healthy',
        timestamp: Date.now(),
        database: 'connected'
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await healthService.check()

      expect(api.get).toHaveBeenCalledWith('/health')
      expect(result).toEqual(mockResponse)
    })

    it('should return status from health check', async () => {
      const mockResponse: HealthCheckResponse = {
        status: 'healthy',
        timestamp: 1234567890,
        database: 'connected'
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await healthService.check()

      expect(result.status).toBe('healthy')
      expect(result.timestamp).toBe(1234567890)
      expect(result.database).toBe('connected')
    })

    it('should handle degraded status', async () => {
      const mockResponse: HealthCheckResponse = {
        status: 'degraded',
        timestamp: Date.now(),
        database: 'slow'
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await healthService.check()

      expect(result.status).toBe('degraded')
      expect(result.database).toBe('slow')
    })

    it('should handle unhealthy status', async () => {
      const mockResponse: HealthCheckResponse = {
        status: 'unhealthy',
        timestamp: Date.now(),
        database: 'disconnected'
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await healthService.check()

      expect(result.status).toBe('unhealthy')
      expect(result.database).toBe('disconnected')
    })

    it('should propagate API errors', async () => {
      const error = new Error('Network error')
      vi.mocked(api.get).mockRejectedValue(error)

      await expect(healthService.check()).rejects.toThrow('Network error')
    })

    it('should handle timeout errors', async () => {
      const timeoutError = new Error('Request timeout')
      vi.mocked(api.get).mockRejectedValue(timeoutError)

      await expect(healthService.check()).rejects.toThrow('Request timeout')
    })

    it('should include timestamp in response', async () => {
      const now = Date.now()
      const mockResponse: HealthCheckResponse = {
        status: 'healthy',
        timestamp: now,
        database: 'connected'
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await healthService.check()

      expect(result.timestamp).toBe(now)
      expect(typeof result.timestamp).toBe('number')
    })

    it('should work without authentication', async () => {
      const mockResponse: HealthCheckResponse = {
        status: 'healthy',
        timestamp: Date.now(),
        database: 'connected'
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      // Health check should not require any auth parameters
      await healthService.check()

      expect(api.get).toHaveBeenCalledWith('/health')
      expect(api.get).toHaveBeenCalledTimes(1)
    })

    it('should handle multiple consecutive checks', async () => {
      const mockResponse1: HealthCheckResponse = {
        status: 'healthy',
        timestamp: 1000,
        database: 'connected'
      }

      const mockResponse2: HealthCheckResponse = {
        status: 'degraded',
        timestamp: 2000,
        database: 'slow'
      }

      vi.mocked(api.get)
        .mockResolvedValueOnce(mockResponse1)
        .mockResolvedValueOnce(mockResponse2)

      const result1 = await healthService.check()
      const result2 = await healthService.check()

      expect(result1.status).toBe('healthy')
      expect(result2.status).toBe('degraded')
      expect(api.get).toHaveBeenCalledTimes(2)
    })

    it('should return complete health check response structure', async () => {
      const mockResponse: HealthCheckResponse = {
        status: 'healthy',
        timestamp: Date.now(),
        database: 'connected'
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await healthService.check()

      expect(result).toHaveProperty('status')
      expect(result).toHaveProperty('timestamp')
      expect(result).toHaveProperty('database')
    })
  })

  describe('edge cases', () => {
    it('should handle empty response gracefully', async () => {
      vi.mocked(api.get).mockResolvedValue({} as HealthCheckResponse)

      const result = await healthService.check()

      expect(result).toBeDefined()
    })

    it('should handle null database status', async () => {
      const mockResponse = {
        status: 'healthy',
        timestamp: Date.now(),
        database: null
      } as any

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await healthService.check()

      expect(result.database).toBeNull()
    })

    it('should handle server errors', async () => {
      const serverError = new Error('500 Internal Server Error')
      vi.mocked(api.get).mockRejectedValue(serverError)

      await expect(healthService.check()).rejects.toThrow('500 Internal Server Error')
    })
  })
})
