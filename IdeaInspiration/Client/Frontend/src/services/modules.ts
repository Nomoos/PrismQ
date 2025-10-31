import api from './api'
import type { Module, ModuleListResponse, ModuleDetailResponse, ModuleConfig } from '@/types/module'
import type { Run } from '@/types/run'

/**
 * Module API service
 */
export const moduleService = {
  /**
   * List all available modules
   */
  async listModules(): Promise<Module[]> {
    const response = await api.get<ModuleListResponse>('/api/modules')
    return response.data.modules
  },

  /**
   * Get details for a specific module
   */
  async getModule(moduleId: string): Promise<Module> {
    const response = await api.get<ModuleDetailResponse>(`/api/modules/${moduleId}`)
    return response.data.module
  },

  /**
   * Get saved configuration for a module
   */
  async getConfig(moduleId: string): Promise<ModuleConfig> {
    try {
      const response = await api.get<ModuleConfig>(`/api/modules/${moduleId}/config`)
      return response.data
    } catch (error) {
      // Return empty config if not found
      return {
        module_id: moduleId,
        parameters: {},
        updated_at: new Date().toISOString()
      }
    }
  },

  /**
   * Save configuration for a module
   */
  async saveConfig(moduleId: string, parameters: Record<string, any>): Promise<void> {
    await api.post(`/api/modules/${moduleId}/config`, { parameters })
  },

  /**
   * Delete saved configuration for a module (reset to defaults)
   */
  async deleteConfig(moduleId: string): Promise<void> {
    await api.delete(`/api/modules/${moduleId}/config`)
  },

  /**
   * Launch a module with parameters
   */
  async launchModule(moduleId: string, parameters: Record<string, any>, saveConfig: boolean = false): Promise<Run> {
    const response = await api.post<Run>(`/api/modules/${moduleId}/run`, {
      parameters,
      save_config: saveConfig
    })
    return response.data
  },
}

export default moduleService
