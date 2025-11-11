import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LoadingSkeleton from '../../src/components/LoadingSkeleton.vue'

describe('LoadingSkeleton.vue', () => {
  describe('rendering', () => {
    it('should render with default props', () => {
      const wrapper = mount(LoadingSkeleton)
      expect(wrapper.find('.skeleton').exists()).toBe(true)
    })

    it('should have text variant by default', () => {
      const wrapper = mount(LoadingSkeleton)
      expect(wrapper.find('.skeleton--text').exists()).toBe(true)
    })

    it('should be animated by default', () => {
      const wrapper = mount(LoadingSkeleton)
      expect(wrapper.find('.skeleton--animated').exists()).toBe(true)
    })
  })

  describe('variants', () => {
    it('should apply text variant', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          variant: 'text'
        }
      })
      expect(wrapper.find('.skeleton--text').exists()).toBe(true)
    })

    it('should apply circular variant', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          variant: 'circular'
        }
      })
      expect(wrapper.find('.skeleton--circular').exists()).toBe(true)
    })

    it('should apply rectangular variant', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          variant: 'rectangular'
        }
      })
      expect(wrapper.find('.skeleton--rectangular').exists()).toBe(true)
    })
  })

  describe('sizing', () => {
    it('should accept width as number', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          width: 200
        }
      })
      const skeleton = wrapper.find('.skeleton')
      expect(skeleton.attributes('style')).toContain('width: 200px')
    })

    it('should accept width as string', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          width: '50%'
        }
      })
      const skeleton = wrapper.find('.skeleton')
      expect(skeleton.attributes('style')).toContain('width: 50%')
    })

    it('should accept height as number', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          height: 100
        }
      })
      const skeleton = wrapper.find('.skeleton')
      expect(skeleton.attributes('style')).toContain('height: 100px')
    })

    it('should accept height as string', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          height: '3rem'
        }
      })
      const skeleton = wrapper.find('.skeleton')
      expect(skeleton.attributes('style')).toContain('height: 3rem')
    })

    it('should accept both width and height', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          width: 150,
          height: 75
        }
      })
      const skeleton = wrapper.find('.skeleton')
      const style = skeleton.attributes('style') || ''
      expect(style).toContain('width: 150px')
      expect(style).toContain('height: 75px')
    })

    it('should handle custom CSS units', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          width: '10vw',
          height: '5vh'
        }
      })
      const skeleton = wrapper.find('.skeleton')
      const style = skeleton.attributes('style') || ''
      expect(style).toContain('width: 10vw')
      expect(style).toContain('height: 5vh')
    })
  })

  describe('animation', () => {
    it('should be animated when animated prop is true', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          animated: true
        }
      })
      expect(wrapper.find('.skeleton--animated').exists()).toBe(true)
    })

    it('should not be animated when animated prop is false', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          animated: false
        }
      })
      expect(wrapper.find('.skeleton--animated').exists()).toBe(false)
    })
  })

  describe('slot', () => {
    it('should render slot content', () => {
      const wrapper = mount(LoadingSkeleton, {
        slots: {
          default: '<span class="custom-content">Loading...</span>'
        }
      })
      expect(wrapper.find('.custom-content').exists()).toBe(true)
      expect(wrapper.text()).toContain('Loading...')
    })

    it('should render without slot content', () => {
      const wrapper = mount(LoadingSkeleton)
      expect(wrapper.find('.skeleton').exists()).toBe(true)
    })
  })

  describe('combined props', () => {
    it('should combine all props correctly', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          variant: 'circular',
          width: 50,
          height: 50,
          animated: false
        }
      })
      
      const skeleton = wrapper.find('.skeleton')
      expect(skeleton.classes()).toContain('skeleton--circular')
      expect(skeleton.classes()).not.toContain('skeleton--animated')
      
      const style = skeleton.attributes('style') || ''
      expect(style).toContain('width: 50px')
      expect(style).toContain('height: 50px')
    })

    it('should handle rectangular skeleton with custom dimensions', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          variant: 'rectangular',
          width: '100%',
          height: 200,
          animated: true
        }
      })
      
      const skeleton = wrapper.find('.skeleton')
      expect(skeleton.classes()).toContain('skeleton--rectangular')
      expect(skeleton.classes()).toContain('skeleton--animated')
      
      const style = skeleton.attributes('style') || ''
      expect(style).toContain('width: 100%')
      expect(style).toContain('height: 200px')
    })
  })

  describe('edge cases', () => {
    it('should handle zero width', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          width: 0
        }
      })
      expect(wrapper.find('.skeleton').attributes('style')).toContain('width: 0px')
    })

    it('should handle zero height', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          height: 0
        }
      })
      expect(wrapper.find('.skeleton').attributes('style')).toContain('height: 0px')
    })

    it('should handle very large dimensions', () => {
      const wrapper = mount(LoadingSkeleton, {
        props: {
          width: 10000,
          height: 10000
        }
      })
      const style = wrapper.find('.skeleton').attributes('style') || ''
      expect(style).toContain('width: 10000px')
      expect(style).toContain('height: 10000px')
    })
  })
})
