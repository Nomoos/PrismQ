/**
 * Accessibility composable for screen reader announcements and focus management
 * Implements WCAG 2.1 AA compliance utilities
 */
import { ref, onUnmounted } from 'vue'

export function useAccessibility() {
  const announcement = ref('')
  let announcementTimeout: ReturnType<typeof setTimeout> | null = null

  /**
   * Announce a message to screen readers
   * @param message - The message to announce
   */
  function announce(message: string) {
    // Clear any existing timeout
    if (announcementTimeout) {
      clearTimeout(announcementTimeout)
    }

    // Set the announcement
    announcement.value = message

    // Clear after 1 second to allow screen readers to read it
    announcementTimeout = setTimeout(() => {
      announcement.value = ''
    }, 1000)
  }

  /**
   * Move focus to an element
   * @param selector - CSS selector or HTMLElement
   * @param options - Focus options
   */
  function moveFocus(
    selector: string | HTMLElement,
    options?: FocusOptions
  ): boolean {
    try {
      const element = typeof selector === 'string' 
        ? document.querySelector<HTMLElement>(selector)
        : selector

      if (element) {
        element.focus(options)
        return true
      }
      return false
    } catch (error) {
      console.warn('Failed to move focus:', error)
      return false
    }
  }

  /**
   * Trap focus within a container (for modals/dialogs)
   * @param containerSelector - The container to trap focus within
   */
  function trapFocus(containerSelector: string) {
    const container = document.querySelector<HTMLElement>(containerSelector)
    if (!container) return () => {}

    const focusableElements = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    
    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        // Shift + Tab: going backwards
        if (document.activeElement === firstElement) {
          e.preventDefault()
          lastElement?.focus()
        }
      } else {
        // Tab: going forwards
        if (document.activeElement === lastElement) {
          e.preventDefault()
          firstElement?.focus()
        }
      }
    }

    container.addEventListener('keydown', handleKeyDown)

    // Focus first element when trap is activated
    firstElement?.focus()

    // Return cleanup function
    return () => {
      container.removeEventListener('keydown', handleKeyDown)
    }
  }

  /**
   * Get all focusable elements within a container
   */
  function getFocusableElements(container: HTMLElement): HTMLElement[] {
    const elements = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    return Array.from(elements).filter(el => {
      return !el.hasAttribute('disabled') && 
             el.offsetParent !== null && // visible
             window.getComputedStyle(el).visibility !== 'hidden'
    })
  }

  /**
   * Create a skip link for keyboard navigation
   */
  function createSkipLink(targetId: string, linkText: string = 'Skip to main content') {
    const skipLink = document.createElement('a')
    skipLink.href = `#${targetId}`
    skipLink.textContent = linkText
    skipLink.className = 'skip-link'
    skipLink.addEventListener('click', (e) => {
      e.preventDefault()
      const target = document.getElementById(targetId)
      if (target) {
        target.tabIndex = -1
        target.focus()
      }
    })
    return skipLink
  }

  // Cleanup on unmount
  onUnmounted(() => {
    if (announcementTimeout) {
      clearTimeout(announcementTimeout)
    }
  })

  return {
    announcement,
    announce,
    moveFocus,
    trapFocus,
    getFocusableElements,
    createSkipLink
  }
}
