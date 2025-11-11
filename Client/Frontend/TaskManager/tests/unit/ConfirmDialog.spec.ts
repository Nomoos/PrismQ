import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ConfirmDialog from '../../src/components/base/ConfirmDialog.vue'

describe('ConfirmDialog.vue', () => {
  let wrapper: any

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('props and emits', () => {
    it('should accept modelValue prop', () => {
      wrapper = mount(ConfirmDialog, {
        props: {
          modelValue: true
        }
      })
      
      expect(wrapper.props('modelValue')).toBe(true)
    })

    it('should accept title prop', () => {
      wrapper = mount(ConfirmDialog, {
        props: {
          modelValue: true,
          title: 'Custom Title'
        }
      })
      
      expect(wrapper.props('title')).toBe('Custom Title')
    })

    it('should accept message prop', () => {
      wrapper = mount(ConfirmDialog, {
        props: {
          modelValue: true,
          message: 'Custom message'
        }
      })
      
      expect(wrapper.props('message')).toBe('Custom message')
    })

    it('should accept confirmText prop', () => {
      wrapper = mount(ConfirmDialog, {
        props: {
          modelValue: true,
          confirmText: 'OK'
        }
      })
      
      expect(wrapper.props('confirmText')).toBe('OK')
    })

    it('should accept cancelText prop', () => {
      wrapper = mount(ConfirmDialog, {
        props: {
          modelValue: true,
          cancelText: 'No'
        }
      })
      
      expect(wrapper.props('cancelText')).toBe('No')
    })

    it('should accept dangerMode prop', () => {
      wrapper = mount(ConfirmDialog, {
        props: {
          modelValue: true,
          dangerMode: true
        }
      })
      
      expect(wrapper.props('dangerMode')).toBe(true)
    })

    it('should have default props', () => {
      wrapper = mount(ConfirmDialog, {
        props: {
          modelValue: true
        }
      })
      
      expect(wrapper.props('title')).toBe('Confirm Action')
      expect(wrapper.props('message')).toBe('Are you sure you want to continue?')
      expect(wrapper.props('confirmText')).toBe('Confirm')
      expect(wrapper.props('cancelText')).toBe('Cancel')
      expect(wrapper.props('dangerMode')).toBe(false)
    })
  })

  describe('component structure', () => {
    it('should mount successfully', () => {
      wrapper = mount(ConfirmDialog, {
        props: {
          modelValue: true
        }
      })
      
      expect(wrapper.exists()).toBe(true)
    })

    it('should be a valid Vue component', () => {
      wrapper = mount(ConfirmDialog, {
        props: {
          modelValue: false
        }
      })
      
      expect(wrapper.vm).toBeDefined()
    })
  })
})
