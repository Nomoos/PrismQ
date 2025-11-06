import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import MultiRunMonitor from '@/components/MultiRunMonitor.vue'
import LogViewer from '@/components/LogViewer.vue'
import type { Run } from '@/types/run'

// Mock the run service
vi.mock('@/services/runs', () => ({
  runService: {
    getRun: vi.fn((runId: string) => {
      return Promise.resolve({
        run_id: runId,
        module_id: 'test-module',
        module_name: 'Test Module',
        status: 'running',
        parameters: {},
        created_at: new Date().toISOString()
      })
    })
  }
}))

// Mock EventSource for LogViewer
class MockEventSource {
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  readyState = 0
  url: string

  constructor(url: string) {
    this.url = url
    setTimeout(() => {
      this.readyState = 1
      if (this.onopen) {
        this.onopen(new Event('open'))
      }
    }, 0)
  }

  close() {
    this.readyState = 2
  }

  static CONNECTING = 0
  static OPEN = 1
  static CLOSED = 2
}

describe('MultiRunMonitor Component', () => {
  let intervalId: number | undefined

  beforeEach(() => {
    // Mock EventSource globally
    global.EventSource = MockEventSource as any
    
    // Clear any existing intervals
    vi.clearAllTimers()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.clearAllTimers()
    vi.useRealTimers()
  })

  it('should render empty state when no runs are monitored', () => {
    const wrapper = mount(MultiRunMonitor)

    expect(wrapper.find('.empty-state').exists()).toBe(true)
    expect(wrapper.text()).toContain('No runs being monitored')
  })

  it('should not show tabs when empty', () => {
    const wrapper = mount(MultiRunMonitor)

    expect(wrapper.find('.tabs').exists()).toBe(false)
  })

  it('should add a run and display it in a tab', async () => {
    const wrapper = mount(MultiRunMonitor)

    const testRun: Run = {
      run_id: 'run-123',
      module_id: 'test-module',
      module_name: 'Test Module',
      status: 'running',
      parameters: {},
      created_at: new Date().toISOString()
    }

    // Add run via exposed method
    wrapper.vm.addRun(testRun)
    await wrapper.vm.$nextTick()

    // Should show tabs
    expect(wrapper.find('.tabs').exists()).toBe(true)
    
    // Should have one tab
    const tabs = wrapper.findAll('.tab')
    expect(tabs).toHaveLength(1)
    
    // Tab should show module name
    expect(tabs[0].text()).toContain('Test Module')
  })

  it('should set the added run as active', async () => {
    const wrapper = mount(MultiRunMonitor)

    const testRun: Run = {
      run_id: 'run-123',
      module_id: 'test-module',
      module_name: 'Test Module',
      status: 'running',
      parameters: {},
      created_at: new Date().toISOString()
    }

    wrapper.vm.addRun(testRun)
    await wrapper.vm.$nextTick()

    // Active tab should have 'active' class
    const activeTab = wrapper.find('.tab.active')
    expect(activeTab.exists()).toBe(true)
    expect(activeTab.text()).toContain('Test Module')
  })

  it('should display LogViewer for active run', async () => {
    const wrapper = mount(MultiRunMonitor)

    const testRun: Run = {
      run_id: 'run-123',
      module_id: 'test-module',
      module_name: 'Test Module',
      status: 'running',
      parameters: {},
      created_at: new Date().toISOString()
    }

    wrapper.vm.addRun(testRun)
    await wrapper.vm.$nextTick()

    // Should have LogViewer component
    const logViewer = wrapper.findComponent(LogViewer)
    expect(logViewer.exists()).toBe(true)
    expect(logViewer.props('runId')).toBe('run-123')
  })

  it('should handle multiple runs', async () => {
    const wrapper = mount(MultiRunMonitor)

    const run1: Run = {
      run_id: 'run-1',
      module_id: 'module-1',
      module_name: 'Module 1',
      status: 'running',
      parameters: {},
      created_at: new Date().toISOString()
    }

    const run2: Run = {
      run_id: 'run-2',
      module_id: 'module-2',
      module_name: 'Module 2',
      status: 'queued',
      parameters: {},
      created_at: new Date().toISOString()
    }

    wrapper.vm.addRun(run1)
    wrapper.vm.addRun(run2)
    await wrapper.vm.$nextTick()

    // Should have two tabs
    const tabs = wrapper.findAll('.tab')
    expect(tabs).toHaveLength(2)
    
    // Should show both module names
    expect(tabs[0].text()).toContain('Module 1')
    expect(tabs[1].text()).toContain('Module 2')
  })

  it('should switch between runs when clicking tabs', async () => {
    const wrapper = mount(MultiRunMonitor)

    const run1: Run = {
      run_id: 'run-1',
      module_id: 'module-1',
      module_name: 'Module 1',
      status: 'running',
      parameters: {},
      created_at: new Date().toISOString()
    }

    const run2: Run = {
      run_id: 'run-2',
      module_id: 'module-2',
      module_name: 'Module 2',
      status: 'running',
      parameters: {},
      created_at: new Date().toISOString()
    }

    wrapper.vm.addRun(run1)
    wrapper.vm.addRun(run2)
    await wrapper.vm.$nextTick()

    // run-2 should be active (last added)
    expect(wrapper.find('.tab.active').text()).toContain('Module 2')
    
    // Click on first tab
    const tabs = wrapper.findAll('.tab')
    await tabs[0].trigger('click')
    await wrapper.vm.$nextTick()
    
    // run-1 should now be active
    expect(wrapper.find('.tab.active').text()).toContain('Module 1')
    
    // LogViewer should show run-1
    const logViewer = wrapper.findComponent(LogViewer)
    expect(logViewer.props('runId')).toBe('run-1')
  })

  it('should close a tab when close button is clicked', async () => {
    const wrapper = mount(MultiRunMonitor)

    const testRun: Run = {
      run_id: 'run-123',
      module_id: 'test-module',
      module_name: 'Test Module',
      status: 'running',
      parameters: {},
      created_at: new Date().toISOString()
    }

    wrapper.vm.addRun(testRun)
    await wrapper.vm.$nextTick()

    // Click close button
    const closeBtn = wrapper.find('.close-btn')
    await closeBtn.trigger('click')
    await wrapper.vm.$nextTick()

    // Should be back to empty state
    expect(wrapper.find('.empty-state').exists()).toBe(true)
    expect(wrapper.find('.tabs').exists()).toBe(false)
  })

  it('should switch to another tab when closing active tab', async () => {
    const wrapper = mount(MultiRunMonitor)

    const run1: Run = {
      run_id: 'run-1',
      module_id: 'module-1',
      module_name: 'Module 1',
      status: 'running',
      parameters: {},
      created_at: new Date().toISOString()
    }

    const run2: Run = {
      run_id: 'run-2',
      module_id: 'module-2',
      module_name: 'Module 2',
      status: 'running',
      parameters: {},
      created_at: new Date().toISOString()
    }

    wrapper.vm.addRun(run1)
    wrapper.vm.addRun(run2)
    await wrapper.vm.$nextTick()

    // run-2 should be active
    expect(wrapper.find('.tab.active').text()).toContain('Module 2')
    
    // Close active tab (run-2)
    const tabs = wrapper.findAll('.tab')
    const closeBtn = tabs[1].find('.close-btn')
    await closeBtn.trigger('click')
    await wrapper.vm.$nextTick()
    
    // Should have only one tab now
    expect(wrapper.findAll('.tab')).toHaveLength(1)
    
    // run-1 should now be active
    expect(wrapper.find('.tab.active').text()).toContain('Module 1')
  })

  it('should show status indicator for each run', async () => {
    const wrapper = mount(MultiRunMonitor)

    const testRun: Run = {
      run_id: 'run-123',
      module_id: 'test-module',
      module_name: 'Test Module',
      status: 'running',
      parameters: {},
      created_at: new Date().toISOString()
    }

    wrapper.vm.addRun(testRun)
    await wrapper.vm.$nextTick()

    // Should have status indicator
    const statusIndicator = wrapper.find('.status-indicator')
    expect(statusIndicator.exists()).toBe(true)
    
    // Running status should have appropriate class
    expect(statusIndicator.classes()).toContain('bg-blue-500')
  })

  it('should not add duplicate runs', async () => {
    const wrapper = mount(MultiRunMonitor)

    const testRun: Run = {
      run_id: 'run-123',
      module_id: 'test-module',
      module_name: 'Test Module',
      status: 'running',
      parameters: {},
      created_at: new Date().toISOString()
    }

    wrapper.vm.addRun(testRun)
    wrapper.vm.addRun(testRun) // Add same run again
    await wrapper.vm.$nextTick()

    // Should still have only one tab
    expect(wrapper.findAll('.tab')).toHaveLength(1)
  })

  it('should clear all runs', async () => {
    const wrapper = mount(MultiRunMonitor)

    const run1: Run = {
      run_id: 'run-1',
      module_id: 'module-1',
      module_name: 'Module 1',
      status: 'running',
      parameters: {},
      created_at: new Date().toISOString()
    }

    const run2: Run = {
      run_id: 'run-2',
      module_id: 'module-2',
      module_name: 'Module 2',
      status: 'running',
      parameters: {},
      created_at: new Date().toISOString()
    }

    wrapper.vm.addRun(run1)
    wrapper.vm.addRun(run2)
    await wrapper.vm.$nextTick()

    // Clear all
    wrapper.vm.clearAll()
    await wrapper.vm.$nextTick()

    // Should be back to empty state
    expect(wrapper.find('.empty-state').exists()).toBe(true)
    expect(wrapper.find('.tabs').exists()).toBe(false)
  })

  it('should remove a specific run', async () => {
    const wrapper = mount(MultiRunMonitor)

    const run1: Run = {
      run_id: 'run-1',
      module_id: 'module-1',
      module_name: 'Module 1',
      status: 'running',
      parameters: {},
      created_at: new Date().toISOString()
    }

    const run2: Run = {
      run_id: 'run-2',
      module_id: 'module-2',
      module_name: 'Module 2',
      status: 'running',
      parameters: {},
      created_at: new Date().toISOString()
    }

    wrapper.vm.addRun(run1)
    wrapper.vm.addRun(run2)
    await wrapper.vm.$nextTick()

    // Remove run-1
    wrapper.vm.removeRun('run-1')
    await wrapper.vm.$nextTick()

    // Should have only one tab
    const tabs = wrapper.findAll('.tab')
    expect(tabs).toHaveLength(1)
    expect(tabs[0].text()).toContain('Module 2')
  })

  it('should apply correct status classes', () => {
    const wrapper = mount(MultiRunMonitor)

    // Test different status colors
    expect(wrapper.vm.getStatusClass('queued')).toContain('bg-yellow-400')
    expect(wrapper.vm.getStatusClass('running')).toContain('bg-blue-500')
    expect(wrapper.vm.getStatusClass('completed')).toContain('bg-green-500')
    expect(wrapper.vm.getStatusClass('failed')).toContain('bg-red-500')
    expect(wrapper.vm.getStatusClass('cancelled')).toContain('bg-gray-400')
    expect(wrapper.vm.getStatusClass('unknown')).toContain('bg-gray-300')
  })
})
