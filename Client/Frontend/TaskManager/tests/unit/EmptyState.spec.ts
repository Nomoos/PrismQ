import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import EmptyState from '@/components/base/EmptyState.vue'

describe('EmptyState Component', () => {
  describe('rendering', () => {
    it('should render with default props', () => {
      const wrapper = mount(EmptyState)
      
      expect(wrapper.text()).toContain('No items found')
      expect(wrapper.text()).toContain('There are no items to display')
      expect(wrapper.text()).toContain('📋')
    })

    it('should render container with proper classes', () => {
      const wrapper = mount(EmptyState)
      
      expect(wrapper.find('.text-center').exists()).toBe(true)
      expect(wrapper.find('.py-8').exists()).toBe(true)
      expect(wrapper.find('.px-4').exists()).toBe(true)
    })
  })

  describe('icon', () => {
    it('should display default icon', () => {
      const wrapper = mount(EmptyState)
      
      expect(wrapper.text()).toContain('📋')
    })

    it('should display custom icon', () => {
      const wrapper = mount(EmptyState, {
        props: {
          icon: '🚀'
        }
      })
      
      expect(wrapper.text()).toContain('🚀')
    })

    it('should not display icon container when icon is not provided', () => {
      const wrapper = mount(EmptyState, {
        props: {
          icon: ''
        }
      })
      
      expect(wrapper.find('.w-16.h-16.rounded-full').exists()).toBe(false)
    })
  })

  describe('title', () => {
    it('should display default title', () => {
      const wrapper = mount(EmptyState)
      
      const title = wrapper.find('h3')
      expect(title.exists()).toBe(true)
      expect(title.text()).toBe('No items found')
    })

    it('should display custom title', () => {
      const wrapper = mount(EmptyState, {
        props: {
          title: 'Custom Title'
        }
      })
      
      const title = wrapper.find('h3')
      expect(title.text()).toBe('Custom Title')
    })

    it('should not display title when not provided', () => {
      const wrapper = mount(EmptyState, {
        props: {
          title: ''
        }
      })
      
      expect(wrapper.find('h3').exists()).toBe(false)
    })
  })

  describe('message', () => {
    it('should display default message', () => {
      const wrapper = mount(EmptyState)
      
      const message = wrapper.find('p')
      expect(message.exists()).toBe(true)
      expect(message.text()).toBe('There are no items to display')
    })

    it('should display custom message', () => {
      const wrapper = mount(EmptyState, {
        props: {
          message: 'Custom message here'
        }
      })
      
      const message = wrapper.find('p')
      expect(message.text()).toBe('Custom message here')
    })

    it('should not display message when not provided', () => {
      const wrapper = mount(EmptyState, {
        props: {
          message: ''
        }
      })
      
      expect(wrapper.find('p').exists()).toBe(false)
    })
  })

  describe('action button', () => {
    it('should display action button when actionText and actionHandler provided', () => {
      const actionHandler = vi.fn()
      const wrapper = mount(EmptyState, {
        props: {
          actionText: 'Click Me',
          actionHandler
        }
      })
      
      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toBe('Click Me')
      expect(button.classes()).toContain('btn-primary')
    })

    it('should call actionHandler when button clicked', async () => {
      const actionHandler = vi.fn()
      const wrapper = mount(EmptyState, {
        props: {
          actionText: 'Click Me',
          actionHandler
        }
      })
      
      await wrapper.find('button').trigger('click')
      
      expect(actionHandler).toHaveBeenCalledTimes(1)
    })

    it('should not display button when actionText is missing', () => {
      const actionHandler = vi.fn()
      const wrapper = mount(EmptyState, {
        props: {
          actionHandler
        }
      })
      
      expect(wrapper.find('button').exists()).toBe(false)
    })

    it('should not display button when actionHandler is missing', () => {
      const wrapper = mount(EmptyState, {
        props: {
          actionText: 'Click Me'
        }
      })
      
      expect(wrapper.find('button').exists()).toBe(false)
    })
  })

  describe('action slot', () => {
    it('should render custom action slot content', () => {
      const wrapper = mount(EmptyState, {
        slots: {
          action: '<a href="/custom">Custom Link</a>'
        }
      })
      
      expect(wrapper.find('a').exists()).toBe(true)
      expect(wrapper.find('a').text()).toBe('Custom Link')
      expect(wrapper.find('button').exists()).toBe(false)
    })

    it('should prefer slot over default action button', () => {
      const actionHandler = vi.fn()
      const wrapper = mount(EmptyState, {
        props: {
          actionText: 'Default Button',
          actionHandler
        },
        slots: {
          action: '<span class="custom-action">Custom Action</span>'
        }
      })
      
      expect(wrapper.find('.custom-action').text()).toBe('Custom Action')
      expect(wrapper.find('button').exists()).toBe(false)
    })
  })

  describe('complete example', () => {
    it('should render all elements together', () => {
      const actionHandler = vi.fn()
      const wrapper = mount(EmptyState, {
        props: {
          icon: '🔍',
          title: 'No Results',
          message: 'Try adjusting your search',
          actionText: 'Clear Filters',
          actionHandler
        }
      })
      
      expect(wrapper.text()).toContain('🔍')
      expect(wrapper.text()).toContain('No Results')
      expect(wrapper.text()).toContain('Try adjusting your search')
      expect(wrapper.find('button').text()).toBe('Clear Filters')
    })
  })
})
