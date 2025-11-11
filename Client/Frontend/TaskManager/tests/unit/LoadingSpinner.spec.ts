import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LoadingSpinner from '@/components/base/LoadingSpinner.vue'

describe('LoadingSpinner Component', () => {
  describe('rendering', () => {
    it('should render with default props', () => {
      const wrapper = mount(LoadingSpinner)
      
      expect(wrapper.find('[role="status"]').exists()).toBe(true)
      expect(wrapper.find('.sr-only').text()).toBe('Loading...')
    })

    it('should render with custom label', () => {
      const wrapper = mount(LoadingSpinner, {
        props: {
          label: 'Processing...'
        }
      })
      
      expect(wrapper.find('.sr-only').text()).toBe('Processing...')
      expect(wrapper.attributes('aria-label')).toBe('Processing...')
    })
  })

  describe('size variations', () => {
    it('should apply small size classes', () => {
      const wrapper = mount(LoadingSpinner, {
        props: { size: 'sm' }
      })
      
      expect(wrapper.classes()).toContain('h-4')
      expect(wrapper.classes()).toContain('w-4')
      expect(wrapper.classes()).toContain('border-2')
    })

    it('should apply medium size classes (default)', () => {
      const wrapper = mount(LoadingSpinner)
      
      expect(wrapper.classes()).toContain('h-8')
      expect(wrapper.classes()).toContain('w-8')
      expect(wrapper.classes()).toContain('border-4')
    })

    it('should apply large size classes', () => {
      const wrapper = mount(LoadingSpinner, {
        props: { size: 'lg' }
      })
      
      expect(wrapper.classes()).toContain('h-12')
      expect(wrapper.classes()).toContain('w-12')
      expect(wrapper.classes()).toContain('border-4')
    })
  })

  describe('color variations', () => {
    it('should apply primary color (default)', () => {
      const wrapper = mount(LoadingSpinner)
      
      expect(wrapper.classes()).toContain('border-primary-500')
    })

    it('should apply white color', () => {
      const wrapper = mount(LoadingSpinner, {
        props: { color: 'white' }
      })
      
      expect(wrapper.classes()).toContain('border-white')
    })

    it('should apply gray color', () => {
      const wrapper = mount(LoadingSpinner, {
        props: { color: 'gray' }
      })
      
      expect(wrapper.classes()).toContain('border-gray-500')
    })
  })

  describe('accessibility', () => {
    it('should have role="status"', () => {
      const wrapper = mount(LoadingSpinner)
      
      expect(wrapper.attributes('role')).toBe('status')
    })

    it('should have aria-label', () => {
      const wrapper = mount(LoadingSpinner, {
        props: { label: 'Custom loading' }
      })
      
      expect(wrapper.attributes('aria-label')).toBe('Custom loading')
    })

    it('should have screen reader text', () => {
      const wrapper = mount(LoadingSpinner, {
        props: { label: 'Loading data' }
      })
      
      const srOnly = wrapper.find('.sr-only')
      expect(srOnly.exists()).toBe(true)
      expect(srOnly.text()).toBe('Loading data')
    })
  })

  describe('animation', () => {
    it('should have animate-spin class', () => {
      const wrapper = mount(LoadingSpinner)
      
      expect(wrapper.classes()).toContain('animate-spin')
    })

    it('should have rounded-full class', () => {
      const wrapper = mount(LoadingSpinner)
      
      expect(wrapper.classes()).toContain('rounded-full')
    })

    it('should have border-t-transparent class', () => {
      const wrapper = mount(LoadingSpinner)
      
      expect(wrapper.classes()).toContain('border-t-transparent')
    })
  })
})
