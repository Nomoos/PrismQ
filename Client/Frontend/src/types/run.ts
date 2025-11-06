/**
 * Run execution status
 */
export type RunStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'

/**
 * Log level
 */
export type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR'

/**
 * Request to start a module run
 */
export interface RunRequest {
  module_id: string
  parameters: Record<string, any>
}

/**
 * Log entry from a module run
 */
export interface LogEntry {
  timestamp: string
  level: LogLevel
  message: string
}

/**
 * Module run information
 */
export interface Run {
  id?: string  // For backward compatibility
  run_id: string
  module_id: string
  module_name: string
  status: RunStatus
  parameters: Record<string, any>
  created_at: string
  started_at?: string
  completed_at?: string
  start_time?: string  // Deprecated, use started_at
  end_time?: string    // Deprecated, use completed_at
  duration_seconds?: number
  progress_percent?: number
  items_processed?: number
  items_total?: number
  exit_code?: number
  error_message?: string
}

/**
 * API response for listing runs
 */
export interface RunListResponse {
  runs: Run[]
  total: number
}

/**
 * API response for run details
 */
export interface RunDetailResponse {
  run: Run
}

/**
 * API response for log entries
 */
export interface LogListResponse {
  logs: LogEntry[]
  total: number
}
