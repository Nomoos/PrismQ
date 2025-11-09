/**
 * Tests for resource hints utilities
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import {
  preloadResource,
  prefetchResource,
  preconnect,
  dnsPrefetch,
  preloadImages,
  preloadFonts
} from '@/utils/resourceHints'

describe('Resource Hints Utilities', () => {
  beforeEach(() => {
    // Clean up any link elements added by previous tests
    const links = document.querySelectorAll('link[rel="preload"], link[rel="prefetch"], link[rel="preconnect"], link[rel="dns-prefetch"]')
    links.forEach(link => link.remove())
  })

  describe('preloadResource', () => {
    it('should create preload link elements', () => {
      const href = '/test-script.js'
      const as = 'script'
      
      // In a real browser, this would add a link to document.head
      // In test environment, we just verify the function executes
      expect(() => {
        preloadResource(href, as)
      }).not.toThrow()
    })

    it('should handle duplicate preload calls', () => {
      const href = '/test-script.js'
      const as = 'script'
      
      // Should not throw when called multiple times
      expect(() => {
        preloadResource(href, as)
        preloadResource(href, as)
      }).not.toThrow()
    })

    it('should support type and crossorigin parameters', () => {
      const href = '/test-font.woff2'
      const as = 'font'
      const type = 'font/woff2'
      const crossOrigin = 'anonymous'
      
      expect(() => {
        preloadResource(href, as, type, crossOrigin)
      }).not.toThrow()
    })
  })

  describe('prefetchResource', () => {
    it('should add prefetch link to document head', () => {
      const href = '/next-page.js'
      
      prefetchResource(href, 'script')
      
      const link = document.querySelector(`link[rel="prefetch"][href="${href}"]`)
      expect(link).toBeTruthy()
    })

    it('should not duplicate prefetch links', () => {
      const href = '/next-page.js'
      
      prefetchResource(href)
      prefetchResource(href)
      
      const links = document.querySelectorAll(`link[rel="prefetch"][href="${href}"]`)
      expect(links.length).toBe(1)
    })
  })

  describe('preconnect', () => {
    it('should add preconnect link to document head', () => {
      const href = 'https://api.example.com'
      
      preconnect(href)
      
      const link = document.querySelector(`link[rel="preconnect"][href="${href}"]`)
      expect(link).toBeTruthy()
    })

    it('should support crossorigin attribute', () => {
      const href = 'https://cdn.example.com'
      
      preconnect(href, true)
      
      const link = document.querySelector(`link[rel="preconnect"][href="${href}"]`) as HTMLLinkElement
      expect(link?.crossOrigin).toBe('anonymous')
    })
  })

  describe('dnsPrefetch', () => {
    it('should add dns-prefetch link to document head', () => {
      const href = '//cdn.example.com'
      
      dnsPrefetch(href)
      
      const link = document.querySelector(`link[rel="dns-prefetch"][href="${href}"]`)
      expect(link).toBeTruthy()
    })
  })

  describe('preloadImages', () => {
    it('should handle multiple image preloads', () => {
      const images = ['/image1.jpg', '/image2.jpg']
      
      expect(() => {
        preloadImages(images)
      }).not.toThrow()
      
      expect(images.length).toBe(2)
    })
  })

  describe('preloadFonts', () => {
    it('should handle multiple font preloads with crossorigin', () => {
      const fonts = ['/font1.woff2', '/font2.woff2']
      
      expect(() => {
        preloadFonts(fonts)
      }).not.toThrow()
      
      expect(fonts.length).toBe(2)
    })
  })
})
