import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import type { Module, ModuleConfig } from '@/types/module'
import type { Run, LogEntry } from '@/types/run'

// Hoist mock functions to ensure they're available before the mock is set up
const { mockGet, mockPost, mockDelete } = vi.hoisted(() => {
  return {
    mockGet: vi.fn(),
    mockPost: vi.fn(),
    mockDelete: vi.fn()
  }
})

// Mock the api module instead of axios directly
vi.mock('@/services/api', () => {
  return {
    default: {
      get: mockGet,
      post: mockPost,
      delete: mockDelete
    }
  }
})

// Import after mocking
const { moduleService } = await import('@/services/modules')
const { runService } = await import('@/services/runs')

describe('Module Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  it('should list modules', async () => {
    const mockModules: Module[] = [
      {
        id: 'test-module',
        name: 'Test Module',
        description: 'Test',
        category: 'Test',
        version: '1.0.0',
        script_path: '/test',
        parameters: [],
        tags: [],
        status: 'active',
        total_runs: 0,
        success_rate: 100,
        enabled: true
      }
    ]

    mockGet.mockResolvedValueOnce({
      data: {
        modules: mockModules,
        total: 1
      }
    })

    const modules = await moduleService.listModules()

    expect(modules).toHaveLength(1)
    expect(modules[0].id).toBe('test-module')
    expect(mockGet).toHaveBeenCalledWith('/api/modules')
  })

  it('should get a specific module', async () => {
    const mockModule: Module = {
      id: 'youtube-shorts',
      name: 'YouTube Shorts',
      description: 'Collect YouTube Shorts',
      category: 'Content/Shorts',
      version: '1.0.0',
      script_path: '/path',
      parameters: [],
      tags: ['youtube', 'shorts'],
      status: 'active',
      total_runs: 10,
      success_rate: 90,
      enabled: true
    }

    mockGet.mockResolvedValueOnce({
      data: {
        module: mockModule
      }
    })

    const module = await moduleService.getModule('youtube-shorts')

    expect(module.id).toBe('youtube-shorts')
    expect(module.name).toBe('YouTube Shorts')
    expect(mockGet).toHaveBeenCalledWith('/api/modules/youtube-shorts')
  })

  it('should get module config', async () => {
    const mockConfig: ModuleConfig = {
      module_id: 'test-module',
      parameters: { max_results: 50 },
      updated_at: new Date().toISOString()
    }

    mockGet.mockResolvedValueOnce({
      data: mockConfig
    })

    const config = await moduleService.getConfig('test-module')

    expect(config.module_id).toBe('test-module')
    expect(config.parameters.max_results).toBe(50)
    expect(mockGet).toHaveBeenCalledWith('/api/modules/test-module/config')
  })

  it('should return empty config when not found', async () => {
    mockGet.mockRejectedValueOnce(new Error('Not found'))

    const config = await moduleService.getConfig('test-module')

    expect(config.module_id).toBe('test-module')
    expect(config.parameters).toEqual({})
  })

  it('should save module config', async () => {
    const parameters = { max_results: 100 }

    mockPost.mockResolvedValueOnce({ data: {} })

    await moduleService.saveConfig('test-module', parameters)

    expect(mockPost).toHaveBeenCalledWith('/api/modules/test-module/config', { parameters })
  })

  it('should launch module', async () => {
    const mockRun: Run = {
      id: 'run-123',
      module_id: 'test-module',
      module_name: 'Test Module',
      status: 'queued',
      parameters: { max_results: 50 },
      start_time: new Date().toISOString()
    }

    mockPost.mockResolvedValueOnce({
      data: mockRun
    })

    const run = await moduleService.launchModule('test-module', { max_results: 50 }, true)

    expect(run.id).toBe('run-123')
    expect(run.status).toBe('queued')
    expect(mockPost).toHaveBeenCalledWith('/api/modules/test-module/run', {
      parameters: { max_results: 50 },
      save_config: true
    })
  })

  it('should handle API errors when listing modules', async () => {
    mockGet.mockRejectedValueOnce(new Error('Network error'))

    await expect(moduleService.listModules()).rejects.toThrow('Network error')
  })

  it('should handle API errors when getting a module', async () => {
    mockGet.mockRejectedValueOnce(new Error('Module not found'))

    await expect(moduleService.getModule('nonexistent')).rejects.toThrow('Module not found')
  })
})

describe('Run Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  it('should list runs', async () => {
    const mockRuns: Run[] = [
      {
        id: 'run-123',
        module_id: 'test-module',
        module_name: 'Test Module',
        status: 'running',
        parameters: { max_results: 50 },
        start_time: '2025-01-01T00:00:00Z'
      }
    ]

    mockGet.mockResolvedValueOnce({
      data: {
        runs: mockRuns,
        total: 1
      }
    })

    const runs = await runService.listRuns()

    expect(runs).toHaveLength(1)
    expect(runs[0].id).toBe('run-123')
    expect(mockGet).toHaveBeenCalledWith('/api/runs', { params: undefined })
  })

  it('should list runs with filters', async () => {
    const mockRuns: Run[] = []

    mockGet.mockResolvedValueOnce({
      data: {
        runs: mockRuns,
        total: 0
      }
    })

    await runService.listRuns({ 
      module_id: 'test-module',
      status: 'completed',
      limit: 10
    })

    expect(mockGet).toHaveBeenCalledWith('/api/runs', {
      params: {
        module_id: 'test-module',
        status: 'completed',
        limit: 10
      }
    })
  })

  it('should get a specific run', async () => {
    const mockRun: Run = {
      id: 'run-123',
      module_id: 'test-module',
      module_name: 'Test Module',
      status: 'completed',
      parameters: { max_results: 50 },
      start_time: '2025-01-01T00:00:00Z',
      end_time: '2025-01-01T00:05:00Z',
      duration_seconds: 300,
      progress_percent: 100
    }

    mockGet.mockResolvedValueOnce({
      data: {
        run: mockRun
      }
    })

    const run = await runService.getRun('run-123')

    expect(run.id).toBe('run-123')
    expect(run.status).toBe('completed')
    expect(mockGet).toHaveBeenCalledWith('/api/runs/run-123')
  })

  it('should cancel a run', async () => {
    mockDelete.mockResolvedValueOnce({ data: {} })

    await runService.cancelRun('run-123')

    expect(mockDelete).toHaveBeenCalledWith('/api/runs/run-123')
  })

  it('should get logs for a run', async () => {
    const mockLogs: LogEntry[] = [
      {
        timestamp: '2025-01-01T00:00:00Z',
        level: 'INFO',
        message: 'Test log message'
      },
      {
        timestamp: '2025-01-01T00:00:01Z',
        level: 'ERROR',
        message: 'Error occurred'
      }
    ]

    mockGet.mockResolvedValueOnce({
      data: {
        logs: mockLogs,
        total: 2
      }
    })

    const logs = await runService.getLogs('run-123')

    expect(logs).toHaveLength(2)
    expect(logs[0].level).toBe('INFO')
    expect(logs[1].level).toBe('ERROR')
    expect(mockGet).toHaveBeenCalledWith('/api/runs/run-123/logs', {
      params: { tail: undefined }
    })
  })

  it('should get logs with tail parameter', async () => {
    mockGet.mockResolvedValueOnce({
      data: {
        logs: [],
        total: 0
      }
    })

    await runService.getLogs('run-123', 100)

    expect(mockGet).toHaveBeenCalledWith('/api/runs/run-123/logs', {
      params: { tail: 100 }
    })
  })

  it('should create a new run', async () => {
    const mockRun: Run = {
      id: 'run-456',
      module_id: 'test-module',
      module_name: 'Test Module',
      status: 'queued',
      parameters: { max_results: 100 },
      start_time: '2025-01-01T00:00:00Z'
    }

    mockPost.mockResolvedValueOnce({
      data: {
        run: mockRun
      }
    })

    const run = await runService.createRun({
      module_id: 'test-module',
      parameters: { max_results: 100 }
    })

    expect(run.id).toBe('run-456')
    expect(run.status).toBe('queued')
    expect(mockPost).toHaveBeenCalledWith('/api/runs', {
      module_id: 'test-module',
      parameters: { max_results: 100 }
    })
  })

  it('should handle errors when getting run', async () => {
    mockGet.mockRejectedValueOnce(new Error('Run not found'))

    await expect(runService.getRun('nonexistent')).rejects.toThrow('Run not found')
  })

  it('should handle errors when canceling run', async () => {
    mockDelete.mockRejectedValueOnce(new Error('Cannot cancel run'))

    await expect(runService.cancelRun('run-123')).rejects.toThrow('Cannot cancel run')
  })
})
