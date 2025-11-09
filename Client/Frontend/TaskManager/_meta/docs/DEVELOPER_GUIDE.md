# TaskManager Developer Guide

**Version**: 0.1.0  
**Last Updated**: 2025-11-09  
**Target Audience**: Developers, Contributors

---

## Table of Contents

1. [Introduction](#introduction)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Architecture Overview](#architecture-overview)
5. [Component Development](#component-development)
6. [State Management](#state-management)
7. [API Integration](#api-integration)
8. [Routing](#routing)
9. [Styling](#styling)
10. [Testing](#testing)
11. [Building & Deployment](#building--deployment)
12. [Contributing](#contributing)

---

## Introduction

### About Frontend/TaskManager

Frontend/TaskManager is a mobile-first Vue 3 web application built with TypeScript and Tailwind CSS. It provides a task management interface for the Backend/TaskManager system.

### Technology Stack

- **Framework**: Vue 3 (Composition API)
- **Language**: TypeScript (Strict Mode)
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router 4
- **Styling**: Tailwind CSS 3
- **HTTP Client**: Axios
- **Testing**: Vitest (unit), Playwright (E2E)
- **Package Manager**: npm

### Key Features

- TypeScript strict mode with 0 errors
- Mobile-first responsive design
- Component-based architecture
- RESTful API integration
- Real-time task updates
- Optimized for performance (< 500KB bundle)

---

## Development Setup

### Prerequisites

Before starting development, ensure you have:

- **Node.js**: Version 18.0.0 or higher
- **npm**: Version 9.0.0 or higher
- **Git**: For version control
- **Code Editor**: VS Code recommended

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd Frontend/TaskManager
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   VITE_API_BASE_URL=http://localhost:8080
   VITE_API_KEY=your-api-key-here
   ```

4. **Start Development Server**
   ```bash
   npm run dev
   ```
   
   The app will be available at `http://localhost:5173`

5. **Verify Installation**
   - Open browser to `http://localhost:5173`
   - You should see the Task List view
   - Check browser console for any errors

### Development Scripts

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Build and analyze bundle size
npm run build:analyze

# Preview production build locally
npm run preview

# Run unit tests
npm run test

# Run tests with coverage report
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Lint and fix code
npm run lint

# Format code with Prettier
npm run format

# Check bundle size
npm run bundle:size
```

---

## Project Structure

### Directory Layout

```
Frontend/TaskManager/
├── _meta/                    # Documentation and planning
│   ├── docs/                 # User and developer docs
│   │   ├── design/          # Design system docs
│   │   ├── USER_GUIDE.md
│   │   ├── DEVELOPER_GUIDE.md
│   │   └── DEPLOYMENT_GUIDE.md
│   └── issues/              # Issue tracking
├── public/                   # Static assets
│   └── favicon.ico
├── scripts/                  # Build and utility scripts
│   └── bundle-size.js
├── src/                      # Application source code
│   ├── assets/              # Images, fonts, etc.
│   ├── composables/         # Reusable composition functions
│   ├── router/              # Vue Router configuration
│   │   └── index.ts
│   ├── services/            # API service layer
│   │   ├── api.ts          # Base API client
│   │   └── taskService.ts  # Task operations
│   ├── stores/              # Pinia stores
│   │   └── taskStore.ts    # Task state management
│   ├── types/               # TypeScript type definitions
│   │   └── task.ts         # Task-related types
│   ├── views/               # Page components
│   │   ├── TaskList.vue
│   │   ├── TaskDetail.vue
│   │   ├── WorkerDashboard.vue
│   │   └── Settings.vue
│   ├── App.vue              # Root component
│   ├── main.ts              # Application entry point
│   └── vite-env.d.ts        # Vite type definitions
├── tests/                    # Test files
│   ├── unit/                # Unit tests
│   └── e2e/                 # E2E tests
├── .env.example             # Environment variable template
├── .gitignore
├── index.html               # HTML entry point
├── package.json             # Dependencies and scripts
├── postcss.config.js        # PostCSS configuration
├── tailwind.config.js       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
├── vite.config.ts           # Vite build configuration
└── vitest.config.ts         # Vitest test configuration
```

### Important Files

- **`src/main.ts`**: Application bootstrap and initialization
- **`src/App.vue`**: Root component with layout and navigation
- **`src/router/index.ts`**: Route definitions
- **`src/services/api.ts`**: Axios configuration and base API client
- **`src/stores/taskStore.ts`**: Central task state management
- **`vite.config.ts`**: Build configuration, code splitting, optimization

---

## Architecture Overview

### Application Architecture

```
┌─────────────────────────────────────────┐
│           User Interface                │
│  (Vue 3 Components + Tailwind CSS)      │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         Vue Router                      │
│  (Client-side routing)                  │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│        Pinia Stores                     │
│  (State Management)                     │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│       Service Layer                     │
│  (API Client + Services)                │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│    Backend/TaskManager API              │
│  (REST API)                             │
└─────────────────────────────────────────┘
```

### Component Hierarchy

```
App.vue
├── TaskList.vue (/)
├── TaskDetail.vue (/tasks/:id)
├── WorkerDashboard.vue (/dashboard)
└── Settings.vue (/settings)
```

### Data Flow

1. **User Action** → Component emits event or calls method
2. **Component** → Calls Pinia store action
3. **Store Action** → Calls service layer
4. **Service** → Makes HTTP request via Axios
5. **API Response** → Service processes response
6. **Store** → Updates state
7. **Component** → Reactively updates UI

---

## Component Development

### Creating a New Component

#### 1. Component File Structure

Create `src/views/MyComponent.vue`:

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// Props
interface Props {
  title: string
  count?: number
}

const props = withDefaults(defineProps<Props>(), {
  count: 0
})

// Emits
interface Emits {
  (e: 'update', value: string): void
  (e: 'close'): void
}

const emit = defineEmits<Emits>()

// State
const isLoading = ref(false)
const data = ref<string[]>([])

// Computed
const hasData = computed(() => data.value.length > 0)

// Methods
const handleClick = () => {
  emit('update', 'new value')
}

// Lifecycle
onMounted(() => {
  // Initialize component
})
</script>

<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">{{ props.title }}</h1>
    
    <div v-if="isLoading">
      <span>Loading...</span>
    </div>
    
    <div v-else-if="hasData">
      <!-- Content -->
    </div>
    
    <div v-else>
      <!-- Empty state -->
    </div>
  </div>
</template>

<style scoped>
/* Component-specific styles if needed */
</style>
```

#### 2. TypeScript Best Practices

- **Always use TypeScript**: Define interfaces for props, emits, and data
- **Strict Mode**: No `any` types (use `unknown` if needed)
- **Type Imports**: Import types separately for clarity
- **Generic Types**: Use for reusable logic

Example:
```typescript
import type { Task, TaskStatus } from '@/types/task'

interface TaskListProps {
  tasks: Task[]
  filter?: TaskStatus
}
```

#### 3. Composition API Patterns

**Reactive State**:
```typescript
import { ref, reactive } from 'vue'

// Primitives
const count = ref(0)
const message = ref('')

// Objects
const state = reactive({
  user: null,
  isLoggedIn: false
})
```

**Computed Properties**:
```typescript
const filteredTasks = computed(() => {
  return tasks.value.filter(task => task.status === 'pending')
})
```

**Watchers**:
```typescript
watch(taskId, async (newId) => {
  await fetchTaskDetails(newId)
})
```

#### 4. Mobile-First Styling

Use Tailwind CSS with mobile-first approach:

```vue
<template>
  <!-- Mobile: full width, Tablet: 2 columns, Desktop: 3 columns -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Touch targets: minimum 44px height -->
    <button class="min-h-[44px] px-4 py-2 bg-blue-500 text-white rounded-lg">
      Tap Me
    </button>
  </div>
</template>
```

---

## State Management

### Pinia Store Structure

Create `src/stores/myStore.ts`:

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MyData } from '@/types/myData'

export const useMyStore = defineStore('my-store', () => {
  // State
  const items = ref<MyData[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters (computed)
  const itemCount = computed(() => items.value.length)
  const hasItems = computed(() => itemCount.value > 0)

  // Actions
  async function fetchItems() {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await myService.getAll()
      items.value = response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function addItem(item: MyData) {
    items.value.push(item)
  }

  function removeItem(id: number) {
    const index = items.value.findIndex(item => item.id === id)
    if (index > -1) {
      items.value.splice(index, 1)
    }
  }

  function reset() {
    items.value = []
    error.value = null
  }

  return {
    // State
    items,
    isLoading,
    error,
    // Getters
    itemCount,
    hasItems,
    // Actions
    fetchItems,
    addItem,
    removeItem,
    reset
  }
})
```

### Using Stores in Components

```vue
<script setup lang="ts">
import { useMyStore } from '@/stores/myStore'
import { storeToRefs } from 'pinia'

const store = useMyStore()

// Get reactive references
const { items, isLoading, error } = storeToRefs(store)

// Call actions directly
const handleRefresh = async () => {
  await store.fetchItems()
}
</script>
```

---

## API Integration

### Base API Client

The base API client (`src/services/api.ts`) is configured with:

- Base URL from environment
- API key authentication
- Request/response interceptors
- Error handling

Example usage:

```typescript
import api from './api'

// GET request
const response = await api.get('/tasks')

// POST request
const newTask = await api.post('/tasks', { type: 'example' })

// PUT request
await api.put(`/tasks/${id}`, { status: 'completed' })

// DELETE request
await api.delete(`/tasks/${id}`)
```

### Creating a Service

Create `src/services/myService.ts`:

```typescript
import api from './api'
import type { MyData, CreateMyDataRequest } from '@/types/myData'

export const myService = {
  async getAll(): Promise<MyData[]> {
    const response = await api.get<MyData[]>('/mydata')
    return response.data
  },

  async getById(id: number): Promise<MyData> {
    const response = await api.get<MyData>(`/mydata/${id}`)
    return response.data
  },

  async create(data: CreateMyDataRequest): Promise<MyData> {
    const response = await api.post<MyData>('/mydata', data)
    return response.data
  },

  async update(id: number, data: Partial<MyData>): Promise<MyData> {
    const response = await api.put<MyData>(`/mydata/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/mydata/${id}`)
  }
}
```

### Error Handling

```typescript
try {
  const data = await myService.getAll()
  // Success
} catch (error) {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      // Server responded with error
      console.error('Server error:', error.response.status)
      console.error('Error data:', error.response.data)
    } else if (error.request) {
      // Request made but no response
      console.error('Network error')
    }
  } else {
    // Other error
    console.error('Unexpected error:', error)
  }
}
```

---

## Routing

### Adding a New Route

Edit `src/router/index.ts`:

```typescript
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/TaskList.vue')
    },
    {
      path: '/my-route',
      name: 'my-route',
      component: () => import('../views/MyView.vue'),
      meta: {
        requiresAuth: true // Custom metadata
      }
    },
    {
      path: '/items/:id',
      name: 'item-detail',
      component: () => import('../views/ItemDetail.vue'),
      props: true // Pass route params as props
    }
  ]
})

export default router
```

### Navigation in Components

```vue
<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Navigate programmatically
const goToDetail = (id: number) => {
  router.push({ name: 'item-detail', params: { id } })
}

// Get route params
const itemId = route.params.id

// Go back
const goBack = () => {
  router.back()
}
</script>

<template>
  <!-- Declarative navigation -->
  <router-link to="/my-route">Go to My Route</router-link>
  <router-link :to="{ name: 'item-detail', params: { id: 123 } }">
    View Item 123
  </router-link>
</template>
```

---

## Styling

### Tailwind CSS

#### Design System Tokens

See `_meta/docs/design/DESIGN_SYSTEM.md` for complete design tokens.

**Colors**:
- Primary: `bg-blue-500`, `text-blue-500`
- Success: `bg-green-500`
- Warning: `bg-yellow-500`
- Error: `bg-red-500`

**Spacing** (8px grid):
- `p-1` = 4px
- `p-2` = 8px
- `p-3` = 12px
- `p-4` = 16px
- `p-6` = 24px

**Typography**:
```html
<h1 class="text-2xl font-bold">Heading 1</h1>
<p class="text-base">Body text (16px minimum)</p>
```

#### Mobile-First Responsive

```html
<!-- Mobile: stack, Tablet+: row -->
<div class="flex flex-col md:flex-row">
  <div class="w-full md:w-1/2">Column 1</div>
  <div class="w-full md:w-1/2">Column 2</div>
</div>

<!-- Show on mobile only -->
<div class="block md:hidden">Mobile only</div>

<!-- Hide on mobile -->
<div class="hidden md:block">Tablet and up</div>
```

#### Custom Configuration

Edit `tailwind.config.js`:

```javascript
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#0ea5e9',
        success: '#22c55e'
      },
      spacing: {
        '18': '4.5rem'
      }
    }
  }
}
```

---

## Testing

### Unit Testing with Vitest

Create `tests/unit/MyComponent.spec.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '@/views/MyComponent.vue'

describe('MyComponent', () => {
  it('renders properly', () => {
    const wrapper = mount(MyComponent, {
      props: {
        title: 'Test Title'
      }
    })
    expect(wrapper.text()).toContain('Test Title')
  })

  it('emits update event on click', async () => {
    const wrapper = mount(MyComponent)
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('update')).toBeTruthy()
  })
})
```

Run tests:
```bash
npm run test
npm run test:coverage
```

### E2E Testing with Playwright

Create `tests/e2e/task-flow.spec.ts`:

```typescript
import { test, expect } from '@playwright/test'

test('can view and claim task', async ({ page }) => {
  await page.goto('/')
  
  // Wait for tasks to load
  await page.waitForSelector('[data-testid="task-card"]')
  
  // Click first task
  await page.click('[data-testid="task-card"]:first-child')
  
  // Should navigate to detail
  await expect(page).toHaveURL(/\/tasks\/\d+/)
  
  // Claim task
  await page.click('button:has-text("Claim Task")')
  
  // Should show complete button
  await expect(page.locator('button:has-text("Complete Task")')).toBeVisible()
})
```

Run E2E tests:
```bash
npm run test:e2e
npm run test:e2e:ui
```

---

## Building & Deployment

### Building for Production

```bash
# Build
npm run build

# Output in dist/
ls -la dist/
```

### Build Configuration

The Vite configuration (`vite.config.ts`) includes:

- **Code Splitting**: Vendor chunks separated
- **Tree Shaking**: Unused code removed
- **Minification**: Terser for JS, cssnano for CSS
- **Asset Optimization**: Images optimized
- **Bundle Analysis**: With `npm run build:analyze`

### Bundle Size Targets

- **Initial bundle**: < 500KB
- **Vendor chunk**: Separated
- **Lazy-loaded routes**: Split per route

Check bundle size:
```bash
npm run bundle:check
```

---

## Contributing

### Code Style

- **TypeScript**: Strict mode, no `any`
- **ESLint**: Run `npm run lint` before committing
- **Prettier**: Run `npm run format` for consistent formatting
- **Commits**: Use conventional commits (feat:, fix:, docs:)

### Pull Request Process

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes
3. Run tests: `npm run test`
4. Lint code: `npm run lint`
5. Build: `npm run build`
6. Commit changes
7. Push and create PR
8. Request review

### Testing Requirements

- Unit tests for new components
- E2E tests for new user flows
- Coverage > 80%

---

## Useful Resources

- [Vue 3 Documentation](https://vuejs.org/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Vite Documentation](https://vitejs.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)

---

**Questions?** Check the project README or contact the development team.
