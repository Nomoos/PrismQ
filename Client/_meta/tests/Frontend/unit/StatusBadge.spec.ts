import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusBadge from '@/components/StatusBadge.vue'
import type { RunStatus } from '@/types/run'

describe('StatusBadge Component', () => {
  it('should render queued status', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'queued' }
    })

    expect(wrapper.text()).toBe('Queued')
    expect(wrapper.find('.status-badge').classes()).toContain('status-queued')
  })

  it('should render running status with animation', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'running' }
    })

    expect(wrapper.text()).toBe('Running...')
    expect(wrapper.find('.status-badge').classes()).toContain('status-running')
  })

  it('should render completed status with checkmark', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'completed' }
    })

    expect(wrapper.text()).toBe('Completed ✓')
    expect(wrapper.find('.status-badge').classes()).toContain('status-completed')
  })

  it('should render failed status with X', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'failed' }
    })

    expect(wrapper.text()).toBe('Failed ✗')
    expect(wrapper.find('.status-badge').classes()).toContain('status-failed')
  })

  it('should render cancelled status', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'cancelled' }
    })

    expect(wrapper.text()).toBe('Cancelled')
    expect(wrapper.find('.status-badge').classes()).toContain('status-cancelled')
  })

  it('should apply correct styling for each status', () => {
    const statuses: RunStatus[] = ['queued', 'running', 'completed', 'failed', 'cancelled']
    
    statuses.forEach(status => {
      const wrapper = mount(StatusBadge, {
        props: { status }
      })
      
      const badge = wrapper.find('.status-badge')
      expect(badge.classes()).toContain(`status-${status}`)
    })
  })
})
