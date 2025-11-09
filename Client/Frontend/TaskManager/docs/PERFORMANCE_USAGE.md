# Performance Optimization - Usage Guide

This guide documents the performance optimization features implemented for Worker04.

## Table of Contents
- [Service Worker (PWA)](#service-worker-pwa)
- [Lazy Loading](#lazy-loading)
- [Resource Hints](#resource-hints)
- [Best Practices](#best-practices)

## Service Worker (PWA)

The service worker provides offline support and caching for better performance.

### Automatic Registration

The service worker is automatically registered in production builds:

```typescript
// src/main.ts
import { registerServiceWorker } from './utils/serviceWorker'

registerServiceWorker({
  onSuccess: () => console.log('Service worker registered'),
  onUpdate: () => console.log('New content available'),
  onOfflineReady: () => console.log('App ready for offline use')
})
```

### Caching Strategies

#### Cache-First (Static Assets)
Scripts, styles, fonts, and images use cache-first strategy:
1. Check cache first
2. Fall back to network if not cached
3. Cache the response for future use

#### Network-First (API & Navigation)
API calls and navigation use network-first strategy:
1. Try network first for fresh data
2. Fall back to cache if offline
3. Update cache with new responses

### Manual Cache Control

```typescript
import { cacheUrls, skipWaitingServiceWorker } from '@/utils/serviceWorker'

// Manually cache specific URLs
await cacheUrls(['/critical-page.js', '/important-image.jpg'])

// Force update to new service worker
await skipWaitingServiceWorker()
```

### Development vs Production

- **Development**: Service worker is disabled (prevents caching issues)
- **Production**: Service worker is active for offline support

## Lazy Loading

### Image Lazy Loading

#### Using LazyImage Component

The simplest way to lazy load images:

```vue
<template>
  <LazyImage
    src="/path/to/large-image.jpg"
    alt="Description"
    width="800"
    height="600"
    :root-margin="'100px'"
  />
</template>

<script setup lang="ts">
import LazyImage from '@/components/LazyImage.vue'
</script>
```

Features:
- Automatic loading when image enters viewport
- Placeholder while loading
- Error handling with fallback
- Smooth fade-in transition
- Native lazy loading support

#### Using Intersection Observer Composable

For custom lazy loading logic:

```vue
<template>
  <img
    ref="elementRef"
    :src="shouldLoad ? actualImage : placeholder"
    loading="lazy"
  />
</template>

<script setup lang="ts">
import { useLazyLoad } from '@/composables/useIntersectionObserver'

const actualImage = '/path/to/image.jpg'
const placeholder = 'data:image/svg+xml,...'

const { elementRef, shouldLoad } = useLazyLoad({
  rootMargin: '50px', // Start loading 50px before visible
  threshold: 0.01      // Trigger when 1% visible
})
</script>
```

### Component Lazy Loading

#### Route-Based Code Splitting

Already implemented in the router:

```typescript
// src/router/index.ts
const routes = [
  {
    path: '/tasks/:id',
    component: () => import('../views/TaskDetail.vue') // Lazy loaded
  }
]
```

#### Dynamic Component Import with Suspense

```vue
<template>
  <Suspense>
    <HeavyComponent />
    <template #fallback>
      <LoadingSkeleton variant="rectangular" height="200px" />
    </template>
  </Suspense>
</template>

<script setup lang="ts">
import { defineAsyncComponent } from 'vue'
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'

const HeavyComponent = defineAsyncComponent(() =>
  import('@/components/HeavyComponent.vue')
)
</script>
```

### Loading Skeleton

Use for better loading UX:

```vue
<template>
  <!-- Text skeleton -->
  <LoadingSkeleton variant="text" width="100%" />
  
  <!-- Circular skeleton (avatar) -->
  <LoadingSkeleton variant="circular" width="40px" height="40px" />
  
  <!-- Rectangular skeleton (image placeholder) -->
  <LoadingSkeleton variant="rectangular" width="100%" height="200px" />
</template>

<script setup lang="ts">
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'
</script>
```

## Resource Hints

Resource hints improve performance by prefetching or preloading resources.

### Preload Critical Resources

Load critical resources as soon as possible:

```typescript
import { preloadResource, preloadImages, preloadFonts } from '@/utils/resourceHints'

// Preload critical script
preloadResource('/critical-script.js', 'script')

// Preload critical images
preloadImages(['/hero-image.jpg', '/logo.png'])

// Preload fonts
preloadFonts(['/fonts/inter-var.woff2'])
```

### Prefetch Future Resources

Load resources that might be needed later:

```typescript
import { prefetchResource } from '@/utils/resourceHints'

// When user hovers over a link, prefetch the next page
function onLinkHover() {
  prefetchResource('/next-page.js', 'script')
}
```

### Preconnect to Origins

Establish early connections to important origins:

```typescript
import { preconnect, dnsPrefetch } from '@/utils/resourceHints'

// Preconnect to API (already in index.html)
preconnect('https://api.prismq.local', true)

// DNS prefetch for CDN
dnsPrefetch('//cdn.example.com')
```

### Smart Preload

Automatically detect resource type:

```typescript
import { smartPreload } from '@/utils/resourceHints'

smartPreload('/assets/critical.js')    // Auto-detected as script
smartPreload('/assets/critical.css')   // Auto-detected as style
smartPreload('/assets/font.woff2')     // Auto-detected as font
```

## Best Practices

### 1. Image Optimization

```vue
<!-- ✅ Good: Lazy loaded with dimensions -->
<LazyImage
  src="/large-image.jpg"
  alt="Description"
  width="800"
  height="600"
/>

<!-- ❌ Bad: No dimensions, causes layout shift -->
<img src="/large-image.jpg" alt="Description" />
```

### 2. Component Loading

```vue
<!-- ✅ Good: Lazy load heavy components -->
<Suspense>
  <template #default>
    <HeavyChart />
  </template>
  <template #fallback>
    <LoadingSkeleton height="400px" />
  </template>
</Suspense>

<!-- ❌ Bad: Import everything upfront -->
<script setup>
import HeavyChart from './HeavyChart.vue'
</script>
```

### 3. Resource Hints

```typescript
// ✅ Good: Preload critical, prefetch optional
preloadResource('/critical.css', 'style')    // Needed now
prefetchResource('/future-page.js', 'script') // Might need later

// ❌ Bad: Preload everything
preloadResource('/everything.js', 'script')  // Wastes bandwidth
```

### 4. Service Worker

```typescript
// ✅ Good: Let service worker handle automatically
// Just register it and let it work

// ❌ Bad: Don't try to override service worker logic
// unless you know what you're doing
```

## Performance Checklist

- [ ] Use `LazyImage` for all images
- [ ] Add `width` and `height` to prevent layout shift
- [ ] Lazy load route components (already done)
- [ ] Use `Suspense` for heavy async components
- [ ] Preload critical resources
- [ ] Prefetch likely next pages
- [ ] Test offline functionality
- [ ] Monitor bundle size with `npm run bundle:check`
- [ ] Run Lighthouse with `npm run lighthouse`

## Troubleshooting

### Service Worker Not Updating

```typescript
import { skipWaitingServiceWorker } from '@/utils/serviceWorker'

// Force update
await skipWaitingServiceWorker()
```

### Images Not Lazy Loading

Check if Intersection Observer is supported:

```typescript
if (!('IntersectionObserver' in window)) {
  console.log('Intersection Observer not supported')
  // Images will load immediately as fallback
}
```

### Resource Hints Not Working

Resource hints are just hints - browsers may ignore them:
- Verify in Network tab that resources are loaded
- Use Performance tab to see timing
- Don't rely on them for critical functionality

## Testing

### Test Service Worker

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Open browser and check:
# - Application > Service Workers
# - Application > Cache Storage
```

### Test Lazy Loading

```bash
# Open DevTools
# Network tab > Throttling > Slow 3G
# Scroll page and watch images load
```

### Test Resource Hints

```bash
# Open DevTools
# Network tab > Filter by type
# Look for "preload" or "prefetch" in Initiator column
```

## Related Documentation

- [Performance Monitoring](./PERFORMANCE.md) - Core Web Vitals tracking
- [Build Configuration](../vite.config.ts) - Vite optimization settings
- [Bundle Analysis](../scripts/bundle-size.js) - Bundle size monitoring
