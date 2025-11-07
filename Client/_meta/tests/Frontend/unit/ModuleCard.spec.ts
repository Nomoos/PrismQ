import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ModuleCard from '@/components/ModuleCard.vue'
import type { Module } from '@/types/module'

describe('ModuleCard Component', () => {
  const mockModule: Module = {
    id: 'test-module',
    name: 'Test Module',
    description: 'A test module for unit testing',
    category: 'Test Category',
    version: '1.0.0',
    script_path: '/test/path',
    parameters: [
      {
        name: 'param1',
        type: 'number',
        default: 10,
        description: 'Test parameter',
        required: true
      }
    ],
    tags: ['test', 'example'],
    status: 'active',
    total_runs: 42,
    success_rate: 95,
    enabled: true
  }

  it('should render module information', () => {
    const wrapper = mount(ModuleCard, {
      props: { module: mockModule }
    })

    expect(wrapper.text()).toContain('Test Module')
    expect(wrapper.text()).toContain('A test module for unit testing')
    expect(wrapper.text()).toContain('Test Category')
  })

  it('should display stats when available', () => {
    const wrapper = mount(ModuleCard, {
      props: { module: mockModule }
    })

    expect(wrapper.text()).toContain('42 runs')
    expect(wrapper.text()).toContain('95% success')
  })

  it('should display tags', () => {
    const wrapper = mount(ModuleCard, {
      props: { module: mockModule }
    })

    expect(wrapper.text()).toContain('test')
    expect(wrapper.text()).toContain('example')
  })

  it('should display version', () => {
    const wrapper = mount(ModuleCard, {
      props: { module: mockModule }
    })

    expect(wrapper.text()).toContain('v1.0.0')
  })

  it('should display status badge', () => {
    const wrapper = mount(ModuleCard, {
      props: { module: mockModule }
    })

    expect(wrapper.text()).toContain('active')
  })

  it('should show "Launch Module" button when enabled and active', () => {
    const wrapper = mount(ModuleCard, {
      props: { module: mockModule }
    })

    const button = wrapper.find('button')
    expect(button.text()).toBe('Launch Module')
    expect(button.attributes('disabled')).toBeUndefined()
  })

  it('should show "Disabled" button when module is disabled', () => {
    const disabledModule = { ...mockModule, enabled: false }
    const wrapper = mount(ModuleCard, {
      props: { module: disabledModule }
    })

    const button = wrapper.find('button')
    expect(button.text()).toBe('Disabled')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('should show "Maintenance" button when status is maintenance', () => {
    const maintenanceModule = { ...mockModule, status: 'maintenance' as const }
    const wrapper = mount(ModuleCard, {
      props: { module: maintenanceModule }
    })

    const button = wrapper.find('button')
    expect(button.text()).toBe('Maintenance')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('should emit launch event with module', async () => {
    const wrapper = mount(ModuleCard, {
      props: { module: mockModule }
    })

    const button = wrapper.find('button')
    await button.trigger('click')

    expect(wrapper.emitted('launch')).toBeTruthy()
    expect(wrapper.emitted('launch')).toHaveLength(1)
    
    const emittedData = wrapper.emitted('launch')?.[0] as [Module]
    expect(emittedData[0]).toEqual(mockModule)
  })

  it('should have module-card class', () => {
    const wrapper = mount(ModuleCard, {
      props: { module: mockModule }
    })

    const card = wrapper.find('.module-card')
    expect(card.exists()).toBe(true)
    expect(card.classes()).toContain('module-card')
  })

  it('should handle modules without tags', () => {
    const noTagsModule = { ...mockModule, tags: [] }
    const wrapper = mount(ModuleCard, {
      props: { module: noTagsModule }
    })

    const tags = wrapper.findAll('.tag')
    expect(tags).toHaveLength(0)
  })

  it('should handle different status values', () => {
    const statuses: ('active' | 'inactive' | 'maintenance')[] = ['active', 'inactive', 'maintenance']
    
    statuses.forEach(status => {
      const testModule = { ...mockModule, status }
      const wrapper = mount(ModuleCard, {
        props: { module: testModule }
      })
      
      expect(wrapper.text()).toContain(status)
    })
  })
})
