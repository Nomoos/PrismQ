/**
 * Module parameter definition
 */
export interface ModuleParameter {
  name: string
  type: 'text' | 'number' | 'select' | 'checkbox' | 'password'
  default?: string | number | boolean
  description: string
  options?: string[]
  required: boolean
  min?: number
  max?: number
}

/**
 * PrismQ module definition
 */
export interface Module {
  id: string
  name: string
  description: string
  category: string
  version: string
  script_path: string
  parameters: ModuleParameter[]
  tags: string[]
  status: 'active' | 'inactive' | 'maintenance'
  last_run?: string
  total_runs: number
  success_rate: number
  enabled: boolean
}

/**
 * API response for listing modules
 */
export interface ModuleListResponse {
  modules: Module[]
  total: number
}

/**
 * API response for module details
 */
export interface ModuleDetailResponse {
  module: Module
}

/**
 * Module configuration
 */
export interface ModuleConfig {
  module_id: string
  parameters: Record<string, any>
  updated_at: string
}
