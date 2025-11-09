/**
 * Intersection Observer composable for lazy loading
 * Detects when elements enter the viewport
 */

import { ref, onMounted, onUnmounted } from 'vue'

export interface IntersectionObserverOptions {
  root?: Element | null
  rootMargin?: string
  threshold?: number | number[]
}

/**
 * Composable to track when an element is visible in viewport
 * Perfect for lazy loading images, components, or triggering animations
 * 
 * @param options Intersection Observer options
 * @returns Object with element ref and visibility state
 * 
 * @example
 * ```vue
 * <script setup>
 * import { useIntersectionObserver } from '@/composables/useIntersectionObserver'
 * 
 * const { elementRef, isIntersecting } = useIntersectionObserver({
 *   rootMargin: '50px' // Start loading 50px before visible
 * })
 * </script>
 * 
 * <template>
 *   <img
 *     ref="elementRef"
 *     :src="isIntersecting ? actualImage : placeholder"
 *     loading="lazy"
 *   />
 * </template>
 * ```
 */
export function useIntersectionObserver(options: IntersectionObserverOptions = {}) {
  const elementRef = ref<Element | null>(null)
  const isIntersecting = ref(false)
  const hasIntersected = ref(false) // Track if it has ever intersected
  let observer: IntersectionObserver | null = null
  
  const defaultOptions: IntersectionObserverOptions = {
    root: null, // viewport
    rootMargin: '0px',
    threshold: 0.01, // Trigger as soon as 1% is visible
    ...options
  }
  
  onMounted(() => {
    if (!elementRef.value) return
    
    // Check if Intersection Observer is supported
    if (!('IntersectionObserver' in window)) {
      // Fallback: assume everything is visible
      isIntersecting.value = true
      hasIntersected.value = true
      return
    }
    
    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          isIntersecting.value = entry.isIntersecting
          
          // Once it has intersected, keep track
          if (entry.isIntersecting) {
            hasIntersected.value = true
          }
        })
      },
      defaultOptions
    )
    
    observer.observe(elementRef.value)
  })
  
  onUnmounted(() => {
    if (observer && elementRef.value) {
      observer.unobserve(elementRef.value)
      observer.disconnect()
    }
  })
  
  return {
    elementRef,
    isIntersecting,
    hasIntersected // Use this if you want to load once and keep loaded
  }
}

/**
 * Simplified composable for one-time lazy loading
 * Once the element is visible, it stays loaded
 * 
 * @param options Intersection Observer options
 * @returns Object with element ref and load state
 * 
 * @example
 * ```vue
 * <script setup>
 * import { useLazyLoad } from '@/composables/useIntersectionObserver'
 * 
 * const { elementRef, shouldLoad } = useLazyLoad()
 * </script>
 * 
 * <template>
 *   <img
 *     ref="elementRef"
 *     :src="shouldLoad ? actualImage : placeholder"
 *     loading="lazy"
 *   />
 * </template>
 * ```
 */
export function useLazyLoad(options: IntersectionObserverOptions = {}) {
  const { elementRef, hasIntersected } = useIntersectionObserver(options)
  
  return {
    elementRef,
    shouldLoad: hasIntersected
  }
}
