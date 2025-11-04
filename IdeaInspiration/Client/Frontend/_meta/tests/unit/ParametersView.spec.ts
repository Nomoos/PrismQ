import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ParametersView from '@/components/ParametersView.vue'

describe('ParametersView Component', () => {
  it('should render parameters', () => {
    const wrapper = mount(ParametersView, {
      props: {
        parameters: {
          max_results: 50,
          channel_id: 'UC123456',
          enabled: true
        }
      }
    })

    expect(wrapper.text()).toContain('max_results')
    expect(wrapper.text()).toContain('50')
    expect(wrapper.text()).toContain('channel_id')
    expect(wrapper.text()).toContain('UC123456')
    expect(wrapper.text()).toContain('enabled')
    expect(wrapper.text()).toContain('true')
  })

  it('should show empty state when no parameters', () => {
    const wrapper = mount(ParametersView, {
      props: {
        parameters: {}
      }
    })

    expect(wrapper.text()).toContain('No parameters specified')
  })

  it('should format null values correctly', () => {
    const wrapper = mount(ParametersView, {
      props: {
        parameters: {
          value: null
        }
      }
    })

    expect(wrapper.text()).toContain('null')
  })

  it('should format object values as JSON', () => {
    const wrapper = mount(ParametersView, {
      props: {
        parameters: {
          config: { nested: 'value', count: 10 }
        }
      }
    })

    const text = wrapper.text()
    expect(text).toContain('config')
    expect(text).toContain('nested')
    expect(text).toContain('value')
  })

  it('should render parameter list when parameters exist', () => {
    const wrapper = mount(ParametersView, {
      props: {
        parameters: {
          param1: 'value1',
          param2: 'value2'
        }
      }
    })

    const parameterItems = wrapper.findAll('.parameter-item')
    expect(parameterItems).toHaveLength(2)
  })

  it('should display parameter keys and values separately', () => {
    const wrapper = mount(ParametersView, {
      props: {
        parameters: {
          test_key: 'test_value'
        }
      }
    })

    const key = wrapper.find('.parameter-key')
    const value = wrapper.find('.parameter-value')

    expect(key.text()).toBe('test_key')
    expect(value.text()).toBe('test_value')
  })
})
