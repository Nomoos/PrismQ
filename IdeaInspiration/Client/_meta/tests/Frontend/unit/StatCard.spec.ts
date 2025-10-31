import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatCard from '@/components/StatCard.vue'

describe('StatCard Component', () => {
  it('should render label and value', () => {
    const wrapper = mount(StatCard, {
      props: {
        label: 'Test Label',
        value: 'Test Value'
      }
    })

    expect(wrapper.text()).toContain('Test Label')
    expect(wrapper.text()).toContain('Test Value')
  })

  it('should render numeric value', () => {
    const wrapper = mount(StatCard, {
      props: {
        label: 'Count',
        value: 42
      }
    })

    expect(wrapper.text()).toContain('Count')
    expect(wrapper.text()).toContain('42')
  })

  it('should render string value', () => {
    const wrapper = mount(StatCard, {
      props: {
        label: 'Status',
        value: 'Running'
      }
    })

    expect(wrapper.text()).toContain('Status')
    expect(wrapper.text()).toContain('Running')
  })

  it('should apply proper styling classes', () => {
    const wrapper = mount(StatCard, {
      props: {
        label: 'Duration',
        value: '2m 30s'
      }
    })

    const card = wrapper.find('.stat-card')
    expect(card.exists()).toBe(true)

    const label = wrapper.find('.stat-label')
    expect(label.exists()).toBe(true)

    const value = wrapper.find('.stat-value')
    expect(value.exists()).toBe(true)
  })
})
