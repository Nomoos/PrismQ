import api from './api'
import type { Run, RunRequest, RunListResponse, RunDetailResponse, LogEntry, LogListResponse } from '@/types/run'

/**
 * Run API service
 */
export const runService = {
  /**
   * List all runs with optional filters
   */
  async listRuns(filters?: {
    module_id?: string
    status?: string
    limit?: number
    offset?: number
  }): Promise<Run[]> {
    const response = await api.get<RunListResponse>('/api/runs', { params: filters })
    return response.data.runs
  },

  /**
   * Get details for a specific run
   */
  async getRun(runId: string): Promise<Run> {
    const response = await api.get<RunDetailResponse>(`/api/runs/${runId}`)
    return response.data.run
  },

  /**
   * Start a new module run
   */
  async createRun(request: RunRequest): Promise<Run> {
    const response = await api.post<RunDetailResponse>('/api/runs', request)
    return response.data.run
  },

  /**
   * Cancel a running module
   */
  async cancelRun(runId: string): Promise<void> {
    await api.delete(`/api/runs/${runId}`)
  },

  /**
   * Get logs for a specific run
   */
  async getLogs(runId: string, tail?: number): Promise<LogEntry[]> {
    const response = await api.get<LogListResponse>(`/api/runs/${runId}/logs`, {
      params: { tail }
    })
    return response.data.logs
  },
}

export default runService
