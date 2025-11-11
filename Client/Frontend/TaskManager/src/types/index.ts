export interface Task {
  id: number
  type: string
  type_id: number
  status: 'pending' | 'claimed' | 'completed' | 'failed'
  params: Record<string, any>
  result: Record<string, any> | null
  error_message: string | null
  priority: number
  attempts: number
  max_attempts: number
  progress: number
  claimed_by: string | null
  claimed_at: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface TaskType {
  id: number
  name: string
  version: string
  param_schema: Record<string, any>
  is_active: boolean
  usage_count?: number
  last_used_at?: string | null
  created_at: string
  updated_at: string
}

export interface Worker {
  id: string
  status: 'active' | 'idle' | 'offline'
  current_task_id: number | null
  last_seen: string
}

export interface ApiResponse<T> {
  success: boolean
  message?: string
  data?: T
  error?: string
}

export interface PaginatedResponse<T> {
  success: boolean
  data: T[]
  pagination: {
    total: number
    page: number
    per_page: number
    total_pages: number
  }
}

// Request types
export interface CreateTaskRequest {
  type: string
  params: Record<string, any>
  priority?: number
}

export interface ClaimTaskRequest {
  worker_id: string
  task_type_id: number
  type_pattern?: string
  sort_by?: 'created_at' | 'priority' | 'id' | 'attempts'
  sort_order?: 'ASC' | 'DESC'
}

export interface CompleteTaskRequest {
  worker_id: string
  success: boolean
  result?: Record<string, any>
  error?: string
}

export interface UpdateProgressRequest {
  worker_id: string
  progress: number
  message?: string
}

// Error types
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public response?: any
  ) {
    super(message)
    this.name = 'APIError'
    Object.setPrototypeOf(this, APIError.prototype)
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'NetworkError'
    Object.setPrototypeOf(this, NetworkError.prototype)
  }
}
