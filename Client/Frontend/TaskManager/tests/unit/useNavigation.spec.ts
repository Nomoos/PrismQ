import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { useNavigation, __resetNavigationState } from '../../src/composables/useNavigation'
import type { NavigationLevel } from '../../src/composables/useNavigation'

describe('useNavigation', () => {
  const STORAGE_KEY = 'prismq_navigation_position'
  const STORAGE_KEY_HISTORY = 'prismq_navigation_history'
  
  beforeEach(() => {
    __resetNavigationState()
  })
  
  afterEach(() => {
    __resetNavigationState()
  })
  
  describe('initialization', () => {
    it('should initialize with PrismQ as default position', () => {
      const navigation = useNavigation()
      expect(navigation.currentPosition.value).toBe('PrismQ')
    })
    
    it('should load saved position from localStorage', () => {
      localStorage.setItem(STORAGE_KEY, 'PrismQ.Idea')
      const navigation = useNavigation()
      expect(navigation.currentPosition.value).toBe('PrismQ.Idea')
    })
    
    it('should fallback to PrismQ if saved position is invalid', () => {
      localStorage.setItem(STORAGE_KEY, 'InvalidLevel')
      const navigation = useNavigation()
      expect(navigation.currentPosition.value).toBe('PrismQ')
    })
  })
  
  describe('breadcrumbs', () => {
    it('should show only root when at PrismQ', () => {
      const navigation = useNavigation()
      const breadcrumbs = navigation.breadcrumbs.value
      
      expect(breadcrumbs).toHaveLength(1)
      expect(breadcrumbs[0].level).toBe('PrismQ')
      expect(breadcrumbs[0].label).toBe('PrismQ')
      expect(breadcrumbs[0].isActive).toBe(true)
    })
    
    it('should show root and child when at child node', () => {
      localStorage.setItem(STORAGE_KEY, 'PrismQ.Idea')
      const navigation = useNavigation()
      const breadcrumbs = navigation.breadcrumbs.value
      
      expect(breadcrumbs).toHaveLength(2)
      expect(breadcrumbs[0].level).toBe('PrismQ')
      expect(breadcrumbs[0].isActive).toBe(false)
      expect(breadcrumbs[1].level).toBe('PrismQ.Idea')
      expect(breadcrumbs[1].label).toBe('Idea')
      expect(breadcrumbs[1].isActive).toBe(true)
    })
  })
  
  describe('available children', () => {
    it('should show all 6 children when at PrismQ root', () => {
      const navigation = useNavigation()
      const children = navigation.availableChildren.value
      
      expect(children).toHaveLength(6)
      expect(children).toContain('PrismQ.Idea')
      expect(children).toContain('PrismQ.IdeaInspiration')
      expect(children).toContain('PrismQ.Draft')
      expect(children).toContain('PrismQ.Script')
      expect(children).toContain('PrismQ.Proofreading')
      expect(children).toContain('PrismQ.Voiceover')
    })
    
    it('should show no children when at child node', () => {
      localStorage.setItem(STORAGE_KEY, 'PrismQ.Idea')
      const navigation = useNavigation()
      const children = navigation.availableChildren.value
      
      expect(children).toHaveLength(0)
    })
  })
  
  describe('parent node', () => {
    it('should have no parent when at PrismQ root', () => {
      const navigation = useNavigation()
      expect(navigation.parentNode.value).toBeNull()
    })
    
    it('should have PrismQ as parent when at child node', () => {
      localStorage.setItem(STORAGE_KEY, 'PrismQ.Draft')
      const navigation = useNavigation()
      expect(navigation.parentNode.value).toBe('PrismQ')
    })
  })
  
  describe('navigation', () => {
    it('should navigate to child node from root', () => {
      const navigation = useNavigation()
      navigation.navigateTo('PrismQ.Script')
      
      expect(navigation.currentPosition.value).toBe('PrismQ.Script')
      expect(localStorage.getItem(STORAGE_KEY)).toBe('PrismQ.Script')
    })
    
    it('should navigate back to parent', () => {
      localStorage.setItem(STORAGE_KEY, 'PrismQ.Voiceover')
      const navigation = useNavigation()
      
      navigation.goToParent()
      
      expect(navigation.currentPosition.value).toBe('PrismQ')
    })
    
    it('should not navigate to parent when at root', () => {
      const navigation = useNavigation()
      navigation.goToParent()
      
      expect(navigation.currentPosition.value).toBe('PrismQ')
    })
  })
  
  describe('history navigation', () => {
    it('should track navigation history', () => {
      const navigation = useNavigation()
      
      navigation.navigateTo('PrismQ.Idea')
      navigation.navigateTo('PrismQ')
      navigation.navigateTo('PrismQ.Script')
      
      expect(navigation.canGoBack.value).toBe(true)
      expect(navigation.canGoForward.value).toBe(false)
    })
    
    it('should go back in history', () => {
      const navigation = useNavigation()
      
      navigation.navigateTo('PrismQ.Idea')
      navigation.navigateTo('PrismQ.Draft')
      
      navigation.goBack()
      
      expect(navigation.currentPosition.value).toBe('PrismQ.Idea')
      expect(navigation.canGoForward.value).toBe(true)
    })
    
    it('should go forward in history', () => {
      const navigation = useNavigation()
      
      navigation.navigateTo('PrismQ.Idea')
      navigation.navigateTo('PrismQ.Draft')
      navigation.goBack()
      navigation.goForward()
      
      expect(navigation.currentPosition.value).toBe('PrismQ.Draft')
    })
    
    it('should not go back when at start of history', () => {
      const navigation = useNavigation()
      expect(navigation.canGoBack.value).toBe(false)
    })
    
    it('should not go forward when at end of history', () => {
      const navigation = useNavigation()
      expect(navigation.canGoForward.value).toBe(false)
    })
  })
  
  describe('reset', () => {
    it('should reset to PrismQ root', () => {
      const navigation = useNavigation()
      
      navigation.navigateTo('PrismQ.Proofreading')
      navigation.reset()
      
      expect(navigation.currentPosition.value).toBe('PrismQ')
    })
    
    it('should clear history on reset', () => {
      const navigation = useNavigation()
      
      navigation.navigateTo('PrismQ.Idea')
      navigation.navigateTo('PrismQ.Draft')
      navigation.reset()
      
      expect(navigation.canGoBack.value).toBe(false)
    })
  })
  
  describe('all navigation levels', () => {
    const allLevels: NavigationLevel[] = [
      'PrismQ',
      'PrismQ.Idea',
      'PrismQ.IdeaInspiration',
      'PrismQ.Draft',
      'PrismQ.Script',
      'PrismQ.Proofreading',
      'PrismQ.Voiceover'
    ]
    
    it('should navigate to all defined levels', () => {
      const navigation = useNavigation()
      
      allLevels.forEach(level => {
        navigation.navigateTo(level)
        expect(navigation.currentPosition.value).toBe(level)
      })
    })
    
    it('should save all levels to localStorage', () => {
      const navigation = useNavigation()
      
      allLevels.forEach(level => {
        navigation.navigateTo(level)
        expect(localStorage.getItem(STORAGE_KEY)).toBe(level)
      })
    })
  })
})
