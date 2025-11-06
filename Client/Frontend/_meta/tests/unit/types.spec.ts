import { describe, it, expect } from 'vitest'
import type { Module, ModuleParameter, ModuleConfig } from '@/types/module'
import type { Run, RunStatus } from '@/types/run'

describe('Module Types', () => {
  it('should create a valid Module object', () => {
    const module: Module = {
      id: 'test-module',
      name: 'Test Module',
      description: 'A test module',
      category: 'Test',
      version: '1.0.0',
      script_path: '/path/to/script.py',
      parameters: [],
      tags: ['test', 'example'],
      status: 'active',
      total_runs: 0,
      success_rate: 100,
      enabled: true
    }

    expect(module.id).toBe('test-module')
    expect(module.name).toBe('Test Module')
    expect(module.enabled).toBe(true)
    expect(module.version).toBe('1.0.0')
    expect(module.status).toBe('active')
    expect(module.tags).toContain('test')
  })

  it('should create a valid ModuleParameter object', () => {
    const param: ModuleParameter = {
      name: 'max_results',
      type: 'number',
      default: 50,
      description: 'Maximum results',
      required: true,
      min: 1,
      max: 100
    }

    expect(param.name).toBe('max_results')
    expect(param.type).toBe('number')
    expect(param.default).toBe(50)
    expect(param.min).toBe(1)
    expect(param.max).toBe(100)
  })

  it('should handle optional ModuleParameter options', () => {
    const param: ModuleParameter = {
      name: 'category',
      type: 'select',
      default: 'All',
      description: 'Category filter',
      options: ['All', 'Gaming', 'Music'],
      required: false
    }

    expect(param.options).toContain('Gaming')
    expect(param.required).toBe(false)
  })

  it('should support all parameter types', () => {
    const types: ModuleParameter['type'][] = ['text', 'number', 'select', 'checkbox', 'password']
    
    types.forEach(type => {
      const param: ModuleParameter = {
        name: 'test',
        type,
        description: 'Test',
        required: false
      }
      expect(param.type).toBe(type)
    })
  })

  it('should create a valid ModuleConfig object', () => {
    const config: ModuleConfig = {
      module_id: 'test-module',
      parameters: { max_results: 50, enabled: true },
      updated_at: new Date().toISOString()
    }

    expect(config.module_id).toBe('test-module')
    expect(config.parameters.max_results).toBe(50)
    expect(config.updated_at).toBeDefined()
  })
})

describe('Run Types', () => {
  it('should create a valid Run object', () => {
    const run: Run = {
      run_id: 'run-123',
      module_id: 'test-module',
      module_name: 'Test Module',
      status: 'queued' as RunStatus,
      parameters: { max_results: 50 },
      created_at: new Date().toISOString()
    }

    expect(run.run_id).toBe('run-123')
    expect(run.status).toBe('queued')
    expect(run.parameters.max_results).toBe(50)
  })

  it('should handle all RunStatus values', () => {
    const statuses: RunStatus[] = ['queued', 'running', 'completed', 'failed', 'cancelled']
    
    statuses.forEach(status => {
      const run: Run = {
        run_id: 'test',
        module_id: 'test',
        module_name: 'Test',
        status,
        parameters: {},
        created_at: new Date().toISOString()
      }
      expect(run.status).toBe(status)
    })
  })

  it('should handle optional Run fields', () => {
    const run: Run = {
      run_id: 'run-123',
      module_id: 'test-module',
      module_name: 'Test Module',
      status: 'completed',
      parameters: {},
      created_at: new Date().toISOString(),
      started_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      exit_code: 0,
      error_message: undefined
    }

    expect(run.started_at).toBeDefined()
    expect(run.completed_at).toBeDefined()
    expect(run.exit_code).toBe(0)
  })
})
