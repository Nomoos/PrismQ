# Frontend/TaskManager - Performance Guide

**Version**: 1.0  
**Last Updated**: 2025-11-09  
**Audience**: Developers

---

## Performance Targets

### Core Metrics

- **Initial Load**: < 3s on 3G
- **Time to Interactive**: < 5s
- **First Contentful Paint**: < 2s
- **Bundle Size**: < 500KB total JavaScript (gzipped)
- **Lighthouse Score**: > 90

### Current Performance

**Bundle Analysis** (Production Build):
- Vue vendor: 90.49 KB (gzipped: 35.35 KB)
- Axios vendor: 38.66 KB (gzipped: 15.50 KB)
- App code: ~25 KB (gzipped: ~7 KB)
- CSS: 12.68 KB (gzipped: 3.12 KB)
- **Total**: ~168 KB (gzipped: ~61 KB) ✅

---

## Optimization Strategies

### 1. Code Splitting

**Route-based Code Splitting**:

```typescript
// router/index.ts
const routes = [
  {
    path: '/',
    component: () => import('../views/TaskList.vue')
  },
  {
    path: '/tasks/:id',
    component: () => import('../views/TaskDetail.vue')
  }
]
```

**Component-based Code Splitting**:

```typescript
// Lazy load heavy components
const HeavyChart = defineAsyncComponent(() =>
  import('./components/HeavyChart.vue')
)
```

### 2. Bundle Optimization

**Manual Chunks** (vite.config.ts):

```typescript
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'vue-vendor': ['vue', 'vue-router', 'pinia'],
        'axios-vendor': ['axios']
      }
    }
  }
}
```

### 3. Tree Shaking

**Use ES6 imports**:

```typescript
// ✅ Good - tree-shakeable
import { ref, computed } from 'vue'

// ❌ Bad - imports everything
import * as Vue from 'vue'
```

### 4. Image Optimization

**Use appropriate formats**:
- WebP for photos (smaller than JPEG)
- SVG for icons and logos
- PNG only when transparency needed

**Lazy loading**:

```vue
<template>
  <img :src="imageUrl" loading="lazy" alt="Description" />
</template>
```

### 5. Caching Strategies

**Service Worker** (future enhancement):

```javascript
// Cache API responses
const CACHE_NAME = 'taskmanager-v1'
const urlsToCache = [
  '/',
  '/assets/index.js',
  '/assets/index.css'
]
```

**HTTP Caching** (.htaccess):

```apache
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/html "access plus 0 seconds"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
</IfModule>
```

### 6. Compression

**Enable gzip** (.htaccess):

```apache
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>
```

### 7. Runtime Performance

**Use v-show vs v-if**:

```vue
<!-- Use v-if when condition rarely changes -->
<div v-if="isVisible">Expensive component</div>

<!-- Use v-show when toggling frequently -->
<div v-show="isVisible">Toggled frequently</div>
```

**Computed vs Methods**:

```vue
<script setup>
// ✅ Good - cached, only recalculates when dependencies change
const filteredTasks = computed(() => 
  tasks.value.filter(t => t.status === 'pending')
)

// ❌ Bad - recalculates on every render
function getFilteredTasks() {
  return tasks.value.filter(t => t.status === 'pending')
}
</script>
```

**Debounce expensive operations**:

```typescript
import { debounce } from 'lodash-es'

const search = debounce((query: string) => {
  // Expensive search operation
}, 300)
```

**Virtual scrolling** (for large lists):

```vue
<template>
  <!-- Only render visible items -->
  <virtual-scroller :items="tasks" :item-height="80">
    <template #default="{ item }">
      <TaskCard :task="item" />
    </template>
  </virtual-scroller>
</template>
```

---

## Monitoring Performance

### Lighthouse

Run Lighthouse audit:

```bash
# Chrome DevTools > Lighthouse > Generate Report
```

Target scores:
- Performance: > 90
- Accessibility: > 90
- Best Practices: > 90
- SEO: > 80

### Bundle Analysis

Analyze bundle size:

```bash
npm run build -- --mode analyze
```

### Chrome DevTools

**Performance Tab**:
1. Record page load
2. Analyze metrics:
   - FCP (First Contentful Paint)
   - LCP (Largest Contentful Paint)
   - TTI (Time to Interactive)
   - TBT (Total Blocking Time)

**Network Tab**:
1. Check resource sizes
2. Identify slow requests
3. Check waterfall diagram

**Coverage Tab**:
1. Identify unused CSS/JS
2. Remove dead code

---

## Mobile Performance

### Mobile-First Approach

Always design for mobile, then enhance for desktop:

```vue
<template>
  <!-- Mobile: Stack vertically -->
  <!-- Desktop: Side by side -->
  <div class="flex flex-col md:flex-row">
    <div class="w-full md:w-1/2">Left</div>
    <div class="w-full md:w-1/2">Right</div>
  </div>
</template>
```

### Reduce JavaScript Execution

**Minimize re-renders**:

```vue
<script setup>
// ✅ Good - memo prevents unnecessary recalculation
const expensiveValue = computed(() => {
  // Heavy computation
  return heavyCalculation()
})

// ❌ Bad - recalculates every time component re-renders
const expensiveValue = () => heavyCalculation()
</script>
```

### Touch Performance

**Passive event listeners** (automatic in Vue 3):

```vue
<template>
  <!-- Vue 3 automatically makes touch listeners passive -->
  <div @touchstart="handleTouch">Touch me</div>
</template>
```

### Network Performance

**Minimize API calls**:

```typescript
// Cache responses
const taskCache = new Map()

async function getTasks() {
  if (taskCache.has('tasks')) {
    return taskCache.get('tasks')
  }
  const tasks = await taskService.list()
  taskCache.set('tasks', tasks)
  return tasks
}
```

**Batch requests**:

```typescript
// ❌ Bad - Multiple requests
await Promise.all([
  taskService.get(1),
  taskService.get(2),
  taskService.get(3)
])

// ✅ Good - Single request
await taskService.getBatch([1, 2, 3])
```

---

## Checklist

### Before Production

- [ ] Run production build: `npm run build`
- [ ] Check bundle size < 500KB
- [ ] Run Lighthouse audit (score > 90)
- [ ] Test on 3G network
- [ ] Test on mobile device
- [ ] Enable compression on server
- [ ] Configure browser caching
- [ ] Remove console.log statements
- [ ] Minify JavaScript and CSS
- [ ] Optimize images
- [ ] Enable HTTPS

### Ongoing Monitoring

- [ ] Monitor bundle size on each release
- [ ] Run Lighthouse monthly
- [ ] Check Core Web Vitals
- [ ] Monitor API response times
- [ ] Track page load times
- [ ] Review user feedback

---

## Best Practices

1. **Keep bundle size small** - Remove unused dependencies
2. **Code split** - Lazy load routes and heavy components
3. **Cache aggressively** - Use HTTP caching and service workers
4. **Optimize images** - Compress and lazy load
5. **Minimize re-renders** - Use computed, memo, and v-show wisely
6. **Debounce inputs** - Reduce API calls from user input
7. **Test on real devices** - Emulators don't show real performance
8. **Monitor metrics** - Track performance over time

---

**Document Owner**: Worker06 (Documentation Specialist)  
**Last Updated**: 2025-11-09  
**Version**: 1.0  
**Status**: ✅ Complete
