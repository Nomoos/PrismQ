# Performance Optimization Guide

A comprehensive guide to maintaining and improving the performance of the Frontend/TaskManager application.

## Table of Contents

1. [Overview](#overview)
2. [Performance Budgets](#performance-budgets)
3. [Build Optimization](#build-optimization)
4. [Code Splitting Strategies](#code-splitting-strategies)
5. [Asset Optimization](#asset-optimization)
6. [Network Optimization](#network-optimization)
7. [Runtime Performance](#runtime-performance)
8. [Monitoring and Testing](#monitoring-and-testing)
9. [Common Pitfalls](#common-pitfalls)
10. [Checklist](#checklist)

## Overview

This guide documents the performance optimization strategies implemented in the Frontend/TaskManager application and provides best practices for maintaining optimal performance as the application evolves.

### Current Performance Status

- **Bundle Size**: 194.10 KB (61% under 500KB budget)
- **Lighthouse Score**: 99/100 (mobile)
- **Load Time (3G)**: 1.5-2.1s
- **Core Web Vitals**: All passing ✅

### Target Audience

This guide is for developers working on the Frontend/TaskManager codebase who need to:
- Add new features without degrading performance
- Optimize existing code for better performance
- Debug performance issues
- Conduct performance audits

## Performance Budgets

### Defined Budgets

Performance budgets are enforced automatically via `scripts/bundle-size.js`:

```javascript
const BUDGETS = {
  initial: 512000,   // 500KB - total JavaScript
  chunk: 102400,     // 100KB - individual chunk warning
  css: 51200,        // 50KB - total CSS
  total: 1048576     // 1MB - total assets
}
```

### Current vs Budget

| Category | Budget | Current | Usage | Headroom |
|----------|--------|---------|-------|----------|
| JavaScript | 500 KB | 194 KB | 39% | 306 KB |
| CSS | 50 KB | 26 KB | 51% | 24 KB |
| Total | 1 MB | 236 KB | 23% | 788 KB |

### Enforcement

Budgets are checked automatically:

```bash
# Check bundle size against budgets
npm run bundle:check

# Analyze bundle composition
npm run build:analyze
```

**Important**: CI/CD pipeline should fail if budgets are exceeded.

## Build Optimization

### Vite Configuration

The application uses Vite with optimized build settings (`vite.config.ts`):

```typescript
export default defineConfig({
  build: {
    target: 'es2015',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info']
      }
    },
    cssCodeSplit: true,
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks(id) {
          // Smart vendor chunking
          if (id.includes('node_modules')) {
            if (id.includes('vue')) return 'vue-vendor'
            if (id.includes('axios')) return 'axios-vendor'
          }
        }
      }
    }
  }
})
```

### Key Optimizations

1. **Terser Minification**
   - Removes all `console.log` statements
   - Strips debugger statements
   - Removes comments
   - Aggressive compression

2. **CSS Code Splitting**
   - Each route has its own CSS chunk
   - Reduces initial CSS payload
   - Improves cache efficiency

3. **Manual Chunking**
   - Framework code in separate vendor chunk
   - HTTP client in separate chunk
   - Better browser caching

4. **No Source Maps in Production**
   - Reduces bundle size
   - Faster builds
   - Re-enable for debugging if needed

### Build Commands

```bash
# Production build
npm run build

# Build with bundle analysis
npm run build:analyze

# Preview production build
npm run preview
```

## Code Splitting Strategies

### Route-Based Splitting

All routes use dynamic imports for automatic code splitting:

```typescript
// src/router/index.ts
const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/TaskList.vue')
  },
  {
    path: '/tasks/:id',
    name: 'task-detail',
    component: () => import('../views/TaskDetail.vue')
  }
]
```

**Benefits**:
- Users only download code for routes they visit
- Faster initial load
- Better cache efficiency

### Component-Level Splitting

For large components used conditionally:

```vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

// Lazy load heavy components
const HeavyChart = defineAsyncComponent(
  () => import('./components/HeavyChart.vue')
)
</script>

<template>
  <HeavyChart v-if="showChart" />
</template>
```

### When to Use Code Splitting

✅ **DO split**:
- Routes (always)
- Large charts or visualization libraries
- Components used in modals/dialogs
- Features behind feature flags
- Admin-only components

❌ **DON'T split**:
- Small components (<5KB)
- Components used on every page
- Critical above-the-fold content
- Frequently accessed features

## Asset Optimization

### Images

#### Lazy Loading

Use native lazy loading for all images:

```vue
<template>
  <!-- Native lazy loading -->
  <img 
    src="/images/task-icon.png" 
    alt="Task icon"
    loading="lazy"
    width="32"
    height="32"
  />
</template>
```

#### Component-Based Lazy Loading

For more control, use the `LazyImage` component:

```vue
<template>
  <LazyImage
    src="/images/worker-avatar.jpg"
    alt="Worker avatar"
    placeholder="/images/placeholder.jpg"
  />
</template>
```

#### Image Optimization Checklist

- [ ] Use appropriate image formats (WebP with fallback)
- [ ] Compress images (TinyPNG, ImageOptim)
- [ ] Use correct dimensions (don't rely on CSS to resize)
- [ ] Implement responsive images with `srcset`
- [ ] Add `width` and `height` attributes (prevents CLS)
- [ ] Use lazy loading for below-the-fold images

### Fonts

Currently using system fonts to avoid network requests:

```css
/* tailwind.config.js */
fontFamily: {
  sans: [
    'system-ui',
    '-apple-system',
    'BlinkMacSystemFont',
    'Segoe UI',
    'Roboto',
    'sans-serif'
  ]
}
```

**If custom fonts are needed**:

```html
<!-- Preload critical fonts -->
<link rel="preload" href="/fonts/custom.woff2" as="font" type="font/woff2" crossorigin>

<!-- Use font-display: swap -->
<style>
@font-face {
  font-family: 'Custom';
  src: url('/fonts/custom.woff2') format('woff2');
  font-display: swap;  /* Prevents invisible text */
}
</style>
```

### CSS

#### Tailwind CSS Optimization

Tailwind automatically removes unused CSS in production:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  // Only includes used classes
}
```

#### CSS Best Practices

- Avoid `@import` in CSS (blocks parallel loading)
- Use CSS modules for component styles
- Critical CSS is inlined in `index.html`
- Non-critical CSS is loaded asynchronously

## Network Optimization

### Resource Hints

Implemented in `index.html`:

```html
<!-- DNS Prefetch - Resolve DNS early -->
<link rel="dns-prefetch" href="//api.prismq.local">

<!-- Preconnect - Establish connection early -->
<link rel="preconnect" href="https://api.prismq.local" crossorigin>
```

### Service Worker Caching

Service worker (`public/sw.js`) provides:
- Offline support
- Asset caching
- API response caching (with fallback)

**Cache Strategy**:
```javascript
// Static assets: Cache first
self.addEventListener('fetch', (event) => {
  if (isStaticAsset(event.request)) {
    event.respondWith(cacheFirst(event.request))
  }
  
  // API calls: Network first with cache fallback
  if (isApiCall(event.request)) {
    event.respondWith(networkFirst(event.request))
  }
})
```

### HTTP/2 Optimization

Ensure server supports HTTP/2:
- Multiplexing (parallel requests)
- Header compression
- Server push (optional)

### API Optimization

```typescript
// Use axios interceptors for caching
axios.interceptors.response.use((response) => {
  // Cache GET requests
  if (response.config.method === 'get') {
    cacheResponse(response)
  }
  return response
})
```

## Runtime Performance

### Vue.js Best Practices

#### 1. Use `v-show` for Frequent Toggles

```vue
<!-- Good: v-show for frequent toggles -->
<div v-show="isVisible">Content</div>

<!-- Good: v-if for conditional rendering -->
<HeavyComponent v-if="showOnce" />
```

#### 2. Computed Properties Over Methods

```vue
<script setup lang="ts">
// Good: Cached computed property
const filteredTasks = computed(() => 
  tasks.value.filter(t => t.status === 'active')
)

// Avoid: Method called on every render
const filteredTasks = () => 
  tasks.value.filter(t => t.status === 'active')
</script>
```

#### 3. Use `v-memo` for Expensive Lists

```vue
<template>
  <div v-for="task in tasks" :key="task.id" v-memo="[task.status]">
    <!-- Only re-renders if task.status changes -->
    <TaskCard :task="task" />
  </div>
</template>
```

#### 4. Optimize Large Lists with Virtual Scrolling

For lists with 100+ items, consider virtual scrolling:

```bash
npm install vue-virtual-scroller
```

```vue
<template>
  <RecycleScroller
    :items="tasks"
    :item-size="80"
    key-field="id"
  >
    <template #default="{ item }">
      <TaskCard :task="item" />
    </template>
  </RecycleScroller>
</template>
```

### Debouncing and Throttling

```typescript
import { debounce } from 'lodash-es'

// Debounce search input
const search = debounce((query: string) => {
  searchTasks(query)
}, 300)

// Throttle scroll handler
const handleScroll = throttle(() => {
  updateScrollPosition()
}, 100)
```

### Avoiding Memory Leaks

```typescript
import { onBeforeUnmount } from 'vue'

// Clean up listeners
onBeforeUnmount(() => {
  eventBus.off('task-updated', handleUpdate)
  clearInterval(pollInterval)
})
```

## Monitoring and Testing

### Lighthouse CI

Run Lighthouse audits automatically:

```bash
# Run Lighthouse CI
npm run lighthouse:ci

# Expected output:
# ✓ Performance: >90
# ✓ FCP: <2s
# ✓ LCP: <3s
# ✓ CLS: <0.1
```

### Performance Tests

```bash
# Run performance tests
npm run test:ux:performance

# Tests include:
# - Load time on 3G network
# - Core Web Vitals
# - Resource loading
# - Memory leaks
```

### Bundle Analysis

```bash
# Generate bundle visualization
npm run build:analyze

# Opens dist/stats.html with:
# - Treemap of bundle composition
# - Gzip and Brotli sizes
# - Duplicate dependencies
```

### Real User Monitoring (RUM)

The app includes `web-vitals` for tracking real user metrics:

```typescript
import { onCLS, onFCP, onLCP } from 'web-vitals'

onCLS((metric) => {
  // Send to analytics
  analytics.track('cls', metric.value)
})
```

### Continuous Monitoring

Set up automated performance checks:

```yaml
# .github/workflows/performance.yml
name: Performance
on: [pull_request]
jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: npm run build
      - run: npm run lighthouse:ci
```

## Common Pitfalls

### 1. ❌ Loading Entire Libraries

```typescript
// Bad: Imports entire lodash (24KB)
import _ from 'lodash'

// Good: Import only what you need
import debounce from 'lodash-es/debounce'
```

### 2. ❌ Unnecessary Re-renders

```vue
<script setup lang="ts">
// Bad: Creates new object on every render
<Component :config="{ theme: 'dark' }" />

// Good: Define outside render
const config = { theme: 'dark' }
<Component :config="config" />
</script>
```

### 3. ❌ Large Dependencies

```bash
# Before adding a dependency, check its size
npm install --save bundle-size-checker
npx bundle-size moment  # 71KB!

# Consider lighter alternatives
npx bundle-size date-fns  # 13KB
npx bundle-size dayjs     # 2KB
```

### 4. ❌ Blocking the Main Thread

```typescript
// Bad: Blocks UI for large datasets
const processed = largeArray.map(expensive)

// Good: Use Web Workers for heavy computation
const worker = new Worker('/worker.js')
worker.postMessage(largeArray)
```

### 5. ❌ Excessive API Calls

```typescript
// Bad: Calls API on every keystroke
watch(searchQuery, async (query) => {
  await searchAPI(query)
})

// Good: Debounce API calls
watch(searchQuery, debounce(async (query) => {
  await searchAPI(query)
}, 300))
```

## Checklist

### Before Adding New Features

- [ ] Check impact on bundle size (`npm run bundle:check`)
- [ ] Use dynamic imports for large features
- [ ] Verify dependencies size before installing
- [ ] Add performance tests for critical paths
- [ ] Run Lighthouse audit (`npm run lighthouse:ci`)

### Before Each Release

- [ ] Run full performance test suite
- [ ] Verify all performance budgets passing
- [ ] Check for bundle size increases
- [ ] Review and optimize any new large dependencies
- [ ] Test on real 3G network (or throttled)
- [ ] Verify Core Web Vitals scores
- [ ] Check for memory leaks (long session testing)

### Code Review Checklist

- [ ] New components use lazy loading where appropriate
- [ ] Images have lazy loading enabled
- [ ] No unnecessary re-renders
- [ ] Computed properties used instead of methods in templates
- [ ] Event listeners cleaned up in `onBeforeUnmount`
- [ ] API calls are debounced/throttled
- [ ] Large lists use virtual scrolling if needed

### Optimization Priorities

1. **High Impact, Low Effort**
   - Enable lazy loading for images
   - Remove unused dependencies
   - Use dynamic imports for routes

2. **High Impact, Medium Effort**
   - Implement code splitting
   - Optimize bundle chunking
   - Add service worker caching

3. **High Impact, High Effort**
   - Implement virtual scrolling
   - Add Web Workers for heavy computation
   - Optimize state management

4. **Medium Impact, Low Effort**
   - Use debounce/throttle
   - Optimize images
   - Minify and compress

## Resources

### Tools

- **Lighthouse**: Performance auditing
- **Chrome DevTools**: Performance profiling
- **Vite Bundle Analyzer**: Visualize bundle composition
- **Bundle Phobia**: Check package sizes before installing

### Documentation

- [Web.dev Performance](https://web.dev/performance/)
- [Vue.js Performance Guide](https://vuejs.org/guide/best-practices/performance.html)
- [Vite Performance](https://vitejs.dev/guide/performance.html)
- [Web Vitals](https://web.dev/vitals/)

### Scripts

```bash
# Performance testing
npm run bundle:check        # Check bundle size
npm run build:analyze       # Analyze bundle composition
npm run lighthouse:ci       # Run Lighthouse audit
npm run test:ux:performance # Run performance tests
npm run perf:test          # Run all performance checks
```

## Conclusion

Maintaining excellent performance requires:
1. **Vigilance**: Monitor budgets and metrics
2. **Discipline**: Follow best practices
3. **Testing**: Regular performance audits
4. **Optimization**: Continuous improvement

The Frontend/TaskManager application currently exceeds all performance targets. By following this guide, you can maintain and improve these metrics as the application grows.

**Remember**: Performance is a feature, not an afterthought!

---

**Last Updated**: November 10, 2025  
**Maintained By**: Frontend Team  
**Questions**: See docs/PERFORMANCE.md or contact Worker04
