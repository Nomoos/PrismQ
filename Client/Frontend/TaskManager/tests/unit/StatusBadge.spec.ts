import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusBadge from '@/components/base/StatusBadge.vue'

describe('StatusBadge Component', () => {
  describe('rendering', () => {
    it('should render with status text', () => {
      const wrapper = mount(StatusBadge, {
        props: {
          status: 'pending'
        }
      })
      
      expect(wrapper.text()).toBe('PENDING')
    })

    it('should render as span element', () => {
      const wrapper = mount(StatusBadge, {
        props: { status: 'pending' }
      })
      
      expect(wrapper.element.tagName).toBe('SPAN')
    })
  })

  describe('status variations', () => {
    it('should apply pending status styles', () => {
      const wrapper = mount(StatusBadge, {
        props: { status: 'pending' }
      })
      
      expect(wrapper.classes()).toContain('bg-yellow-100')
      expect(wrapper.classes()).toContain('text-yellow-800')
    })

    it('should apply claimed status styles', () => {
      const wrapper = mount(StatusBadge, {
        props: { status: 'claimed' }
      })
      
      expect(wrapper.classes()).toContain('bg-blue-100')
      expect(wrapper.classes()).toContain('text-blue-800')
    })

    it('should apply completed status styles', () => {
      const wrapper = mount(StatusBadge, {
        props: { status: 'completed' }
      })
      
      expect(wrapper.classes()).toContain('bg-green-100')
      expect(wrapper.classes()).toContain('text-green-800')
    })

    it('should apply failed status styles', () => {
      const wrapper = mount(StatusBadge, {
        props: { status: 'failed' }
      })
      
      expect(wrapper.classes()).toContain('bg-red-100')
      expect(wrapper.classes()).toContain('text-red-800')
    })

    it('should apply active status styles', () => {
      const wrapper = mount(StatusBadge, {
        props: { status: 'active' }
      })
      
      expect(wrapper.classes()).toContain('bg-green-100')
      expect(wrapper.classes()).toContain('text-green-800')
    })

    it('should apply idle status styles', () => {
      const wrapper = mount(StatusBadge, {
        props: { status: 'idle' }
      })
      
      expect(wrapper.classes()).toContain('bg-yellow-100')
      expect(wrapper.classes()).toContain('text-yellow-800')
    })

    it('should apply offline status styles', () => {
      const wrapper = mount(StatusBadge, {
        props: { status: 'offline' }
      })
      
      expect(wrapper.classes()).toContain('bg-gray-100')
      expect(wrapper.classes()).toContain('text-gray-800')
    })

    it('should apply default styles for unknown status', () => {
      const wrapper = mount(StatusBadge, {
        props: { status: 'unknown' }
      })
      
      expect(wrapper.classes()).toContain('bg-gray-100')
      expect(wrapper.classes()).toContain('text-gray-800')
    })

    it('should handle case-insensitive status', () => {
      const wrapper = mount(StatusBadge, {
        props: { status: 'PENDING' }
      })
      
      expect(wrapper.classes()).toContain('bg-yellow-100')
      expect(wrapper.classes()).toContain('text-yellow-800')
    })
  })

  describe('text formatting', () => {
    it('should display uppercase text by default', () => {
      const wrapper = mount(StatusBadge, {
        props: { status: 'pending' }
      })
      
      expect(wrapper.text()).toBe('PENDING')
    })

    it('should display original case when uppercase is false', () => {
      const wrapper = mount(StatusBadge, {
        props: {
          status: 'pending',
          uppercase: false
        }
      })
      
      expect(wrapper.text()).toBe('pending')
    })

    it('should preserve mixed case when uppercase is false', () => {
      const wrapper = mount(StatusBadge, {
        props: {
          status: 'InProgress',
          uppercase: false
        }
      })
      
      expect(wrapper.text()).toBe('InProgress')
    })
  })

  describe('styling', () => {
    it('should have base badge classes', () => {
      const wrapper = mount(StatusBadge, {
        props: { status: 'pending' }
      })
      
      expect(wrapper.classes()).toContain('inline-block')
      expect(wrapper.classes()).toContain('px-2')
      expect(wrapper.classes()).toContain('py-1')
      expect(wrapper.classes()).toContain('rounded')
      expect(wrapper.classes()).toContain('text-xs')
      expect(wrapper.classes()).toContain('font-medium')
    })
  })
})
