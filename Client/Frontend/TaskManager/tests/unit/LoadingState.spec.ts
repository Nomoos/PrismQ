import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LoadingState from '../../src/components/base/LoadingState.vue'
import LoadingSpinner from '../../src/components/base/LoadingSpinner.vue'

describe('LoadingState.vue', () => {
  it('renders loading message', () => {
    const wrapper = mount(LoadingState, {
      props: {
        message: 'Loading data...'
      },
      global: {
        components: {
          LoadingSpinner
        }
      }
    })
    
    expect(wrapper.text()).toContain('Loading data...')
  })
  
  it('uses default message when not provided', () => {
    const wrapper = mount(LoadingState, {
      global: {
        components: {
          LoadingSpinner
        }
      }
    })
    
    expect(wrapper.text()).toContain('Loading...')
  })
  
  it('renders LoadingSpinner component', () => {
    const wrapper = mount(LoadingState, {
      global: {
        components: {
          LoadingSpinner
        }
      }
    })
    
    expect(wrapper.findComponent(LoadingSpinner).exists()).toBe(true)
  })
  
  it('passes size prop to LoadingSpinner', () => {
    const wrapper = mount(LoadingState, {
      props: {
        size: 'sm'
      },
      global: {
        components: {
          LoadingSpinner
        }
      }
    })
    
    const spinner = wrapper.findComponent(LoadingSpinner)
    expect(spinner.props('size')).toBe('sm')
  })
  
  it('applies correct padding class for small padding', () => {
    const wrapper = mount(LoadingState, {
      props: {
        padding: 'sm'
      },
      global: {
        components: {
          LoadingSpinner
        }
      }
    })
    
    expect(wrapper.classes()).toContain('py-4')
  })
  
  it('applies correct padding class for medium padding', () => {
    const wrapper = mount(LoadingState, {
      props: {
        padding: 'md'
      },
      global: {
        components: {
          LoadingSpinner
        }
      }
    })
    
    expect(wrapper.classes()).toContain('py-6')
  })
  
  it('applies correct padding class for large padding (default)', () => {
    const wrapper = mount(LoadingState, {
      global: {
        components: {
          LoadingSpinner
        }
      }
    })
    
    expect(wrapper.classes()).toContain('py-8')
  })
  
  it('has correct ARIA attributes', () => {
    const wrapper = mount(LoadingState, {
      global: {
        components: {
          LoadingSpinner
        }
      }
    })
    
    const container = wrapper.find('[role="status"]')
    expect(container.exists()).toBe(true)
    expect(container.attributes('aria-live')).toBe('polite')
  })
  
  it('hides message when empty string provided', () => {
    const wrapper = mount(LoadingState, {
      props: {
        message: ''
      },
      global: {
        components: {
          LoadingSpinner
        }
      }
    })
    
    const paragraph = wrapper.find('p')
    expect(paragraph.exists()).toBe(false)
  })
})
