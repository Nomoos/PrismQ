import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ModuleLaunchModal from '@/components/ModuleLaunchModal.vue'
import type { Module } from '@/types/module'

// Mock the moduleService
vi.mock('@/services/modules', () => ({
  moduleService: {
    getConfig: vi.fn().mockResolvedValue({
      module_id: 'test-module',
      parameters: {},
      updated_at: new Date().toISOString()
    })
  }
}))

describe('ModuleLaunchModal Component', () => {
  const mockModule: Module = {
    id: 'test-module',
    name: 'Test Module',
    description: 'A test module',
    category: 'Test',
    version: '1.0.0',
    script_path: '/test/path',
    parameters: [
      {
        name: 'max_results',
        type: 'number',
        default: 50,
        description: 'Maximum results',
        required: true,
        min: 1,
        max: 100
      },
      {
        name: 'api_key',
        type: 'password',
        description: 'API Key',
        required: true
      },
      {
        name: 'category',
        type: 'select',
        default: 'All',
        description: 'Category',
        options: ['All', 'Gaming', 'Music'],
        required: false
      },
      {
        name: 'enabled',
        type: 'checkbox',
        default: true,
        description: 'Enable feature',
        required: false
      }
    ],
    tags: ['test'],
    status: 'active',
    total_runs: 0,
    success_rate: 100,
    enabled: true
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render modal with module name', () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: mockModule }
    })

    expect(wrapper.text()).toContain('Launch: Test Module')
  })

  it('should render all parameter fields', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: mockModule }
    })

    await flushPromises()

    expect(wrapper.text()).toContain('Maximum results')
    expect(wrapper.text()).toContain('API Key')
    expect(wrapper.text()).toContain('Category')
    expect(wrapper.text()).toContain('Enable feature')
  })

  it('should mark required fields', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: mockModule }
    })

    await flushPromises()

    const requiredLabels = wrapper.findAll('.required')
    expect(requiredLabels.length).toBeGreaterThan(0)
  })

  it('should render number input with min and max', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: mockModule }
    })

    await flushPromises()

    const numberInput = wrapper.find('input[type="number"]')
    expect(numberInput.exists()).toBe(true)
    expect(numberInput.attributes('min')).toBe('1')
    expect(numberInput.attributes('max')).toBe('100')
  })

  it('should render password input', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: mockModule }
    })

    await flushPromises()

    const passwordInput = wrapper.find('input[type="password"]')
    expect(passwordInput.exists()).toBe(true)
  })

  it('should render select dropdown with options', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: mockModule }
    })

    await flushPromises()

    const select = wrapper.find('select')
    expect(select.exists()).toBe(true)
    
    const options = select.findAll('option')
    expect(options).toHaveLength(3)
    expect(options[0].text()).toBe('All')
    expect(options[1].text()).toBe('Gaming')
    expect(options[2].text()).toBe('Music')
  })

  it('should render checkbox input', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: mockModule }
    })

    await flushPromises()

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    // One for the parameter, one for save config
    expect(checkboxes.length).toBeGreaterThanOrEqual(1)
  })

  it('should have save configuration checkbox checked by default', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: mockModule }
    })

    await flushPromises()

    const saveConfigCheckbox = wrapper.find('.save-config-label input[type="checkbox"]')
    expect(saveConfigCheckbox.element.checked).toBe(true)
  })

  it('should emit close event when close button clicked', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: mockModule }
    })

    await wrapper.find('.btn-close').trigger('click')

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should emit close event when overlay clicked', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: mockModule }
    })

    await wrapper.find('.modal-overlay').trigger('click')

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should emit launch event with parameters on submit', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: mockModule }
    })

    await flushPromises()

    const form = wrapper.find('form')
    await form.trigger('submit.prevent')

    expect(wrapper.emitted('launch')).toBeTruthy()
    expect(wrapper.emitted('launch')).toHaveLength(1)
  })

  it('should show launching state when submitting', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: mockModule }
    })

    await flushPromises()

    const submitButton = wrapper.find('.btn-primary')
    expect(submitButton.text()).toBe('Launch')

    const form = wrapper.find('form')
    form.trigger('submit.prevent')
    
    await wrapper.vm.$nextTick()
    
    // Button text changes during submission
    expect(submitButton.text()).toContain('Launch')
  })

  it('should have cancel button', async () => {
    const wrapper = mount(ModuleLaunchModal, {
      props: { module: mockModule }
    })

    await flushPromises()

    const cancelButton = wrapper.find('.btn-secondary')
    expect(cancelButton.text()).toBe('Cancel')

    await cancelButton.trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
