import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ErrorDisplay from '../../src/components/base/ErrorDisplay.vue'

describe('ErrorDisplay.vue', () => {
  it('renders error message', () => {
    const wrapper = mount(ErrorDisplay, {
      props: {
        message: 'Test error message'
      }
    })
    
    expect(wrapper.text()).toContain('Test error message')
  })
  
  it('shows retry button by default', () => {
    const wrapper = mount(ErrorDisplay, {
      props: {
        message: 'Error'
      }
    })
    
    const button = wrapper.find('button')
    expect(button.exists()).toBe(true)
    expect(button.text()).toBe('Retry')
  })
  
  it('hides retry button when retryable is false', () => {
    const wrapper = mount(ErrorDisplay, {
      props: {
        message: 'Error',
        retryable: false
      }
    })
    
    const button = wrapper.find('button')
    expect(button.exists()).toBe(false)
  })
  
  it('uses custom retry label', () => {
    const wrapper = mount(ErrorDisplay, {
      props: {
        message: 'Error',
        retryLabel: 'Try Again'
      }
    })
    
    const button = wrapper.find('button')
    expect(button.text()).toBe('Try Again')
  })
  
  it('emits retry event when button is clicked', async () => {
    const wrapper = mount(ErrorDisplay, {
      props: {
        message: 'Error'
      }
    })
    
    const button = wrapper.find('button')
    await button.trigger('click')
    
    expect(wrapper.emitted('retry')).toBeTruthy()
    expect(wrapper.emitted('retry')?.length).toBe(1)
  })
  
  it('has correct ARIA attributes', () => {
    const wrapper = mount(ErrorDisplay, {
      props: {
        message: 'Error'
      }
    })
    
    const container = wrapper.find('[role="alert"]')
    expect(container.exists()).toBe(true)
    expect(container.attributes('aria-live')).toBe('assertive')
  })
})
