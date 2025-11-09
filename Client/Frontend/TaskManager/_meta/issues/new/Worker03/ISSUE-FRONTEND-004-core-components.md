# ISSUE-FRONTEND-004: Core Components & Architecture

## Status
🔴 NOT STARTED

## Component
Frontend (Core Components)

## Type
Component Development / Architecture

## Priority
High

## Assigned To
Worker03 - Vue.js/TypeScript Expert

## Description
Implement the core Vue 3 component library using Composition API and TypeScript strict mode. Build all essential UI components for the task management interface following the mobile-first design system from Worker11.

## Problem Statement
The Frontend needs:
- Vue 3 component library with Composition API
- TypeScript strict mode for type safety
- Mobile-first, reusable components
- Consistent component architecture
- Vue Router configuration
- Composables for common patterns
- Integration with Pinia stores

## Solution
Build comprehensive component library including:
1. Task components (list, detail, creation)
2. Worker components (dashboard, status)
3. Common UI components (buttons, forms, modals)
4. Mobile-specific components (bottom sheets, swipe actions)
5. Vue Router setup with mobile navigation
6. Composables for task management, mobile detection
7. TypeScript strict mode configuration

## Deliverables

### Core Components

#### Task Components
- [ ] TaskList.vue - Mobile-optimized task list
- [ ] TaskCard.vue - Individual task card with swipe actions
- [ ] TaskDetail.vue - Full task detail view
- [ ] TaskCreateForm.vue - Mobile-friendly task creation
- [ ] TaskProgress.vue - Progress indicator component
- [ ] TaskStatusBadge.vue - Status indicator (pending, claimed, completed, failed)

#### Worker Components
- [ ] WorkerDashboard.vue - Worker overview and stats
- [ ] WorkerStatus.vue - Worker status indicator
- [ ] WorkerTaskList.vue - Worker's claimed tasks

#### Common Components
- [ ] BaseButton.vue - Primary button component (44px min height)
- [ ] BaseInput.vue - Form input with validation
- [ ] BaseSelect.vue - Dropdown select
- [ ] BaseModal.vue - Modal/bottom sheet for mobile
- [ ] BaseCard.vue - Card container
- [ ] BaseSpinner.vue - Loading indicator
- [ ] BaseBadge.vue - Status badge
- [ ] BaseToast.vue - Toast notification

#### Mobile Components
- [ ] BottomSheet.vue - Mobile bottom sheet modal
- [ ] SwipeAction.vue - Swipeable action container
- [ ] PullToRefresh.vue - Pull-to-refresh component
- [ ] MobileNav.vue - Bottom navigation bar
- [ ] TouchFeedback.vue - Touch feedback wrapper

### Views
- [ ] TaskListView.vue - Main task list page
- [ ] TaskDetailView.vue - Task detail page
- [ ] TaskCreateView.vue - Task creation page
- [ ] WorkerDashboardView.vue - Worker dashboard page
- [ ] SettingsView.vue - Settings page

### Composables
- [ ] useTask.ts - Task management composable
- [ ] useWorker.ts - Worker management composable
- [ ] useMobile.ts - Mobile detection and utilities
- [ ] useToast.ts - Toast notification composable
- [ ] useSwipe.ts - Swipe gesture handling
- [ ] useInfiniteScroll.ts - Infinite scroll/pagination

### Router
- [ ] router/index.ts - Vue Router configuration
- [ ] Mobile-first navigation structure
- [ ] Route guards for authentication
- [ ] Lazy loading for code splitting

### TypeScript
- [ ] tsconfig.json - TypeScript strict mode
- [ ] Type definitions for all components
- [ ] Props and emits with full typing
- [ ] Composable return types

### Tests
- [ ] Unit tests for all components (Vitest)
- [ ] Component tests with Vue Test Utils
- [ ] Composable tests
- [ ] Coverage > 80%

## Acceptance Criteria
- [ ] All core components implemented
- [ ] Components follow mobile-first design from Worker11
- [ ] TypeScript strict mode with 0 errors
- [ ] All components have prop types and emit types
- [ ] Vue Router configured with lazy loading
- [ ] Composables tested and documented
- [ ] Unit test coverage > 80%
- [ ] Components responsive (mobile to desktop)
- [ ] Touch targets ≥ 44x44px
- [ ] Accessibility attributes (ARIA labels)
- [ ] Component documentation complete

## Dependencies
- **Blocks**: ISSUE-FRONTEND-002 (UX Design) - needs design specs
- **Backend API**: Backend/TaskManager (already complete)

## Enables
- ISSUE-FRONTEND-005 (Performance) - needs components to optimize
- ISSUE-FRONTEND-007 (Testing) - needs components to test
- ISSUE-FRONTEND-008 (UX Review) - needs components to review

## Technical Details

### Component Architecture

#### Composition API Pattern
```typescript
// Example component structure
<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Task } from '@/types/task'

interface Props {
  task: Task
  showActions?: boolean
}

interface Emits {
  (e: 'claim', taskId: string): void
  (e: 'complete', taskId: string): void
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true
})

const emit = defineEmits<Emits>()

// Component logic here
</script>
```

#### File Structure
```
src/
├── components/
│   ├── tasks/
│   │   ├── TaskList.vue
│   │   ├── TaskCard.vue
│   │   ├── TaskDetail.vue
│   │   └── __tests__/
│   │       ├── TaskList.spec.ts
│   │       └── TaskCard.spec.ts
│   ├── workers/
│   │   └── WorkerDashboard.vue
│   ├── common/
│   │   ├── BaseButton.vue
│   │   ├── BaseInput.vue
│   │   └── __tests__/
│   └── mobile/
│       ├── BottomSheet.vue
│       └── SwipeAction.vue
├── composables/
│   ├── useTask.ts
│   ├── useWorker.ts
│   └── __tests__/
│       └── useTask.spec.ts
├── views/
│   ├── TaskListView.vue
│   └── TaskDetailView.vue
└── router/
    └── index.ts
```

### Component Specifications

#### TaskCard Component
- **Size**: Minimum 72px height
- **Touch Target**: Full card (min 44px touch zone)
- **Content**: Title, status badge, priority, timestamp
- **Actions**: Swipe right to claim, tap for details
- **States**: Default, claimed, completed, failed, loading
- **Responsive**: Single column mobile, grid on desktop

#### BaseButton Component
- **Height**: 44px minimum
- **Padding**: 12px horizontal
- **Border Radius**: 8px
- **Variants**: Primary, secondary, danger, ghost
- **States**: Default, hover, active, disabled, loading
- **Accessibility**: Focus indicator, ARIA label support

#### BottomSheet Component
- **Mobile**: Slides up from bottom
- **Desktop**: Shows as centered modal
- **Backdrop**: Dismissible by tap
- **Animation**: Smooth 300ms transition
- **Accessibility**: Focus trap, ESC to close

### Vue Router Configuration

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'TaskList',
    component: () => import('@/views/TaskListView.vue')
  },
  {
    path: '/tasks/:id',
    name: 'TaskDetail',
    component: () => import('@/views/TaskDetailView.vue')
  },
  {
    path: '/tasks/create',
    name: 'TaskCreate',
    component: () => import('@/views/TaskCreateView.vue')
  },
  {
    path: '/worker',
    name: 'WorkerDashboard',
    component: () => import('@/views/WorkerDashboardView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

### Composables Pattern

```typescript
// composables/useTask.ts
import { ref, computed } from 'vue'
import { useTaskStore } from '@/stores/tasks'
import type { Task } from '@/types/task'

export function useTask(taskId?: string) {
  const store = useTaskStore()
  const loading = ref(false)
  const error = ref<string | null>(null)

  const task = computed(() => 
    taskId ? store.getTaskById(taskId) : null
  )

  async function claimTask(id: string) {
    loading.value = true
    error.value = null
    try {
      await store.claimTask(id)
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  return {
    task,
    loading,
    error,
    claimTask
  }
}
```

### TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

## Mobile-First Implementation

### Touch Optimization
- All interactive elements ≥ 44x44px
- Tap targets with adequate spacing (8px minimum)
- Touch feedback on all buttons (active state)
- Swipe gestures for common actions
- Long press for secondary actions

### Responsive Design
- Mobile-first CSS (320px base)
- Breakpoints: 640px, 768px, 1024px, 1280px
- Single column on mobile
- Grid layouts on tablet/desktop
- Hide/show elements based on screen size

### Performance
- Lazy load routes (code splitting)
- Lazy load heavy components
- Virtual scrolling for long lists
- Debounce search/filter inputs
- Optimize re-renders with v-memo

## Testing Strategy

### Unit Tests
```typescript
// TaskCard.spec.ts
import { mount } from '@vue/test-utils'
import TaskCard from '@/components/tasks/TaskCard.vue'

describe('TaskCard', () => {
  it('renders task title', () => {
    const task = { id: '1', title: 'Test Task', status: 'pending' }
    const wrapper = mount(TaskCard, { props: { task } })
    expect(wrapper.text()).toContain('Test Task')
  })

  it('emits claim event on button click', async () => {
    const task = { id: '1', title: 'Test', status: 'pending' }
    const wrapper = mount(TaskCard, { props: { task } })
    await wrapper.find('[data-test="claim-btn"]').trigger('click')
    expect(wrapper.emitted('claim')).toBeTruthy()
  })
})
```

## Timeline
- **Start**: After Worker11 completes ISSUE-FRONTEND-002
- **Duration**: 1 week (Week 2)
- **Target**: Week 2 completion

## Progress Tracking
- [ ] Project setup (Vite, Vue 3, TypeScript)
- [ ] Router configuration
- [ ] Base components (10 components)
- [ ] Task components (6 components)
- [ ] Worker components (3 components)
- [ ] Mobile components (5 components)
- [ ] Views (5 views)
- [ ] Composables (6 composables)
- [ ] Unit tests (>80% coverage)
- [ ] Documentation

## Success Criteria
- ✅ All components implemented and tested
- ✅ TypeScript strict mode with 0 errors
- ✅ Unit test coverage > 80%
- ✅ Mobile-first and responsive
- ✅ Touch-optimized (44x44px targets)
- ✅ Accessible (ARIA labels, keyboard nav)
- ✅ Performance optimized (lazy loading)
- ✅ Approved by Worker10 (Code Review)

## Notes
- Follow design system from Worker11 (ISSUE-FRONTEND-002)
- Integrate with Pinia stores from Worker02 (ISSUE-FRONTEND-003)
- Components should be reusable and well-documented
- Mobile-first: design for Redmi 24115RA8EG first
- Focus on touch interactions and gestures
- Keep bundle size minimal with code splitting

---

**Created By**: Worker01 (Project Manager)  
**Date**: 2025-11-09  
**Assigned To**: Worker03 (Vue.js/TypeScript Expert)  
**Status**: 🔴 NOT STARTED  
**Priority**: High (critical path item - depends on Worker11)
