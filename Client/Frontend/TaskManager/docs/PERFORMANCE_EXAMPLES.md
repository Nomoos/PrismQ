# Performance Optimization Examples

This document shows practical examples of using the performance features in views and components.

## Example 1: Lazy Loading Images in Task List

```vue
<template>
  <div class="task-list">
    <div v-for="task in tasks" :key="task.id" class="task-item">
      <!-- Regular content loads immediately -->
      <h3>{{ task.title }}</h3>
      <p>{{ task.description }}</p>
      
      <!-- Lazy load task image when it comes into view -->
      <LazyImage
        v-if="task.imageUrl"
        :src="task.imageUrl"
        :alt="task.title"
        width="400"
        height="300"
        :root-margin="'100px'"
        class="task-image"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import LazyImage from '@/components/LazyImage.vue'

interface Task {
  id: number
  title: string
  description: string
  imageUrl?: string
}

const tasks = ref<Task[]>([])
</script>
```

## Example 2: Lazy Loading Heavy Component

```vue
<template>
  <div class="dashboard">
    <h1>Worker Dashboard</h1>
    
    <!-- Basic info loads immediately -->
    <div class="quick-stats">
      <div>Active: {{ activeWorkers }}</div>
      <div>Pending: {{ pendingTasks }}</div>
    </div>
    
    <!-- Heavy chart component lazy loads with skeleton -->
    <Suspense>
      <template #default>
        <PerformanceChart :data="chartData" />
      </template>
      <template #fallback>
        <LoadingSkeleton variant="rectangular" width="100%" height="400px" />
      </template>
    </Suspense>
  </div>
</template>

<script setup lang="ts">
import { ref, defineAsyncComponent } from 'vue'
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'

// Lazy load heavy chart component
const PerformanceChart = defineAsyncComponent(() =>
  import('@/components/charts/PerformanceChart.vue')
)

const activeWorkers = ref(5)
const pendingTasks = ref(23)
const chartData = ref([])
</script>
```

## Example 3: Prefetch Next Route on Hover

```vue
<template>
  <nav>
    <RouterLink
      to="/tasks"
      @mouseenter="prefetchTasks"
    >
      Tasks
    </RouterLink>
    
    <RouterLink
      to="/workers"
      @mouseenter="prefetchWorkers"
    >
      Workers
    </RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { prefetchResource } from '@/utils/resourceHints'

// Prefetch route chunks when user hovers over link
function prefetchTasks() {
  // This will load the TaskList component chunk early
  prefetchResource('/assets/TaskList-*.js', 'script')
}

function prefetchWorkers() {
  // This will load the WorkerDashboard component chunk early
  prefetchResource('/assets/WorkerDashboard-*.js', 'script')
}
</script>
```

## Example 4: Custom Lazy Loading with Intersection Observer

```vue
<template>
  <div class="stats-grid">
    <!-- Only load stats when section is visible -->
    <div ref="elementRef" class="stats-section">
      <template v-if="shouldLoad">
        <div v-for="stat in stats" :key="stat.id" class="stat-card">
          <h3>{{ stat.value }}</h3>
          <p>{{ stat.label }}</p>
        </div>
      </template>
      <template v-else>
        <LoadingSkeleton
          v-for="i in 4"
          :key="i"
          variant="rectangular"
          height="100px"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useLazyLoad } from '@/composables/useIntersectionObserver'
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'

const { elementRef, shouldLoad } = useLazyLoad({
  rootMargin: '200px', // Start loading 200px before visible
  threshold: 0.1
})

const stats = ref([])

// Load data when component becomes visible
watch(shouldLoad, (isVisible) => {
  if (isVisible && stats.value.length === 0) {
    loadStatsData()
  }
})

async function loadStatsData() {
  // Fetch stats from API
  // stats.value = await fetchStats()
}
</script>
```

## Example 5: Progressive Image Loading

```vue
<template>
  <div class="task-detail">
    <h1>{{ task.title }}</h1>
    
    <!-- Use low-res placeholder that transitions to high-res -->
    <picture>
      <source
        :srcset="shouldLoad ? task.imageHigh : task.imageLow"
        type="image/webp"
      />
      <img
        ref="elementRef"
        :src="shouldLoad ? task.imageHigh : task.imageLow"
        :alt="task.title"
        :class="{ 'loaded': hasLoaded }"
        @load="hasLoaded = true"
        width="800"
        height="600"
      />
    </picture>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useLazyLoad } from '@/composables/useIntersectionObserver'

const { elementRef, shouldLoad } = useLazyLoad()
const hasLoaded = ref(false)

const task = ref({
  title: 'Task Name',
  imageLow: '/images/task-low.jpg',   // 10KB placeholder
  imageHigh: '/images/task-high.jpg'  // 200KB full image
})
</script>

<style scoped>
img {
  opacity: 0.5;
  transition: opacity 0.3s ease-in-out;
}

img.loaded {
  opacity: 1;
}
</style>
```

## Example 6: Preload Critical Resources

```vue
<template>
  <div class="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { preloadFonts, preloadImages, preconnect } from '@/utils/resourceHints'

onMounted(() => {
  // Preload critical fonts
  preloadFonts(['/fonts/inter-var.woff2'])
  
  // Preload hero images
  preloadImages(['/images/hero.webp', '/images/logo.webp'])
  
  // Preconnect to API for faster first request
  preconnect('https://api.prismq.local', true)
})
</script>
```

## Example 7: Loading States with Skeleton

```vue
<template>
  <div class="task-card">
    <template v-if="loading">
      <!-- Skeleton while loading -->
      <div class="skeleton-card">
        <LoadingSkeleton variant="circular" width="40px" height="40px" />
        <div style="flex: 1; margin-left: 12px;">
          <LoadingSkeleton variant="text" width="80%" />
          <LoadingSkeleton variant="text" width="60%" />
        </div>
      </div>
    </template>
    
    <template v-else>
      <!-- Actual content -->
      <img :src="task.avatar" class="avatar" />
      <div>
        <h3>{{ task.title }}</h3>
        <p>{{ task.description }}</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'

const loading = ref(true)
const task = ref({})

onMounted(async () => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000))
  task.value = { /* data */ }
  loading.value = false
})
</script>
```

## Example 8: Service Worker Status Indicator

```vue
<template>
  <div class="app-header">
    <h1>TaskManager</h1>
    
    <!-- Show offline status -->
    <div v-if="isOffline" class="offline-banner">
      <span>⚠️ You are offline. Some features may be limited.</span>
    </div>
    
    <!-- Show update available -->
    <div v-if="updateAvailable" class="update-banner">
      <span>🎉 New version available!</span>
      <button @click="updateApp">Update Now</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { registerServiceWorker, skipWaitingServiceWorker } from '@/utils/serviceWorker'

const isOffline = ref(!navigator.onLine)
const updateAvailable = ref(false)

onMounted(() => {
  // Listen for online/offline events
  window.addEventListener('online', () => isOffline.value = false)
  window.addEventListener('offline', () => isOffline.value = true)
  
  // Register service worker and listen for updates
  registerServiceWorker({
    onUpdate: () => {
      updateAvailable.value = true
    }
  })
})

async function updateApp() {
  await skipWaitingServiceWorker()
  // Page will reload automatically
}
</script>
```

## Performance Best Practices Summary

1. **Images**: Always use `LazyImage` for non-critical images
2. **Components**: Lazy load heavy components with `defineAsyncComponent`
3. **Routes**: Already lazy loaded via router
4. **Skeletons**: Show loading states instead of blank spaces
5. **Prefetch**: Prefetch likely next pages on hover
6. **Preload**: Preload critical resources in App.vue
7. **Service Worker**: Let it work automatically, just handle updates
8. **Offline**: Show appropriate UI for offline state

## Testing Your Optimizations

```bash
# 1. Check bundle size
npm run bundle:check

# 2. Run Lighthouse audit
npm run lighthouse

# 3. Test on slow network
# Open DevTools > Network > Throttling > Slow 3G

# 4. Test service worker
npm run build
npm run preview
# Check DevTools > Application > Service Workers
```
