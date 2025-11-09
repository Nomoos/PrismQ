/**
 * Resource hints utilities
 * Dynamically add preload, prefetch, and preconnect hints
 */

/**
 * Preload a critical resource
 * Use for resources needed for the current page
 * 
 * @param href URL of the resource
 * @param as Type of resource (script, style, image, font, etc.)
 * @param type MIME type (optional)
 * @param crossOrigin Cross-origin setting (optional)
 * 
 * @example
 * preloadResource('/assets/critical-font.woff2', 'font', 'font/woff2', 'anonymous')
 */
export function preloadResource(
  href: string,
  as: string,
  type?: string,
  crossOrigin?: 'anonymous' | 'use-credentials'
) {
  // Check if already preloaded
  const existing = document.querySelector(`link[rel="preload"][href="${href}"]`)
  if (existing) return
  
  const link = document.createElement('link')
  link.rel = 'preload'
  link.href = href
  link.as = as
  
  if (type) {
    link.type = type
  }
  
  if (crossOrigin) {
    link.crossOrigin = crossOrigin
  }
  
  document.head.appendChild(link)
}

/**
 * Prefetch a resource for future navigation
 * Use for resources that might be needed later
 * 
 * @param href URL of the resource
 * @param as Type of resource (optional)
 * 
 * @example
 * prefetchResource('/next-page.js', 'script')
 */
export function prefetchResource(href: string, as?: string) {
  // Check if already prefetched
  const existing = document.querySelector(`link[rel="prefetch"][href="${href}"]`)
  if (existing) return
  
  const link = document.createElement('link')
  link.rel = 'prefetch'
  link.href = href
  
  if (as) {
    link.as = as
  }
  
  document.head.appendChild(link)
}

/**
 * Preconnect to an origin
 * Establishes early connection to important third-party origins
 * 
 * @param href Origin URL
 * @param crossOrigin Whether to use CORS
 * 
 * @example
 * preconnect('https://api.example.com')
 */
export function preconnect(href: string, crossOrigin = false) {
  // Check if already connected
  const existing = document.querySelector(`link[rel="preconnect"][href="${href}"]`)
  if (existing) return
  
  const link = document.createElement('link')
  link.rel = 'preconnect'
  link.href = href
  
  if (crossOrigin) {
    link.crossOrigin = 'anonymous'
  }
  
  document.head.appendChild(link)
}

/**
 * DNS prefetch for an origin
 * Resolves DNS early for important third-party origins
 * 
 * @param href Origin URL
 * 
 * @example
 * dnsPrefetch('//cdn.example.com')
 */
export function dnsPrefetch(href: string) {
  // Check if already prefetched
  const existing = document.querySelector(`link[rel="dns-prefetch"][href="${href}"]`)
  if (existing) return
  
  const link = document.createElement('link')
  link.rel = 'dns-prefetch'
  link.href = href
  
  document.head.appendChild(link)
}

/**
 * Prefetch the next route in Vue Router
 * 
 * @param routeName Route name to prefetch
 * 
 * @example
 * prefetchRoute('task-detail')
 */
export function prefetchRoute(routeName: string) {
  // This is a placeholder - actual implementation would need
  // to access the router's chunk mapping
  console.log(`[Resource Hints] Prefetch route: ${routeName}`)
  // In a real implementation, you'd get the chunk name from Vite's manifest
  // and call prefetchResource with the correct URL
}

/**
 * Preload critical images
 * 
 * @param images Array of image URLs
 * @param imageType MIME type (default: image/jpeg)
 * 
 * @example
 * preloadImages(['/hero-image.jpg', '/logo.png'])
 */
export function preloadImages(images: string[], imageType = 'image/jpeg') {
  images.forEach((src) => {
    preloadResource(src, 'image', imageType)
  })
}

/**
 * Preload critical fonts
 * 
 * @param fonts Array of font URLs
 * @param fontType MIME type (default: font/woff2)
 * 
 * @example
 * preloadFonts(['/fonts/inter-var.woff2'])
 */
export function preloadFonts(fonts: string[], fontType = 'font/woff2') {
  fonts.forEach((src) => {
    preloadResource(src, 'font', fontType, 'anonymous')
  })
}

/**
 * Helper to get resource type from URL
 * 
 * @param url URL of the resource
 * @returns Resource type
 */
function getResourceType(url: string): string {
  const extension = url.split('.').pop()?.toLowerCase()
  
  switch (extension) {
    case 'js':
    case 'mjs':
      return 'script'
    case 'css':
      return 'style'
    case 'woff':
    case 'woff2':
    case 'ttf':
    case 'otf':
      return 'font'
    case 'jpg':
    case 'jpeg':
    case 'png':
    case 'gif':
    case 'webp':
    case 'svg':
      return 'image'
    default:
      return 'fetch'
  }
}

/**
 * Smart preload based on URL
 * Automatically determines resource type
 * 
 * @param url URL of the resource
 * 
 * @example
 * smartPreload('/assets/critical-script.js')
 */
export function smartPreload(url: string) {
  const type = getResourceType(url)
  preloadResource(url, type)
}
