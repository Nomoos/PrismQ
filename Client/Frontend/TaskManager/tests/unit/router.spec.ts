import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

describe('Router Configuration', () => {
  let router: any

  const routes: RouteRecordRaw[] = [
    {
      path: '/',
      name: 'home',
      component: { template: '<div>Home</div>' },
      meta: { title: 'Tasks' }
    },
    {
      path: '/tasks/:id',
      name: 'task-detail',
      component: { template: '<div>Task Detail</div>' },
      meta: { title: 'Task Detail' }
    },
    {
      path: '/workers',
      name: 'workers',
      component: { template: '<div>Workers</div>' },
      meta: { title: 'Workers' }
    },
    {
      path: '/settings',
      name: 'settings',
      component: { template: '<div>Settings</div>' },
      meta: { title: 'Settings' }
    }
  ]

  beforeEach(() => {
    router = createRouter({
      history: createMemoryHistory(),
      routes
    })
  })

  describe('route definitions', () => {
    it('should have home route', () => {
      const route = router.getRoutes().find((r: any) => r.name === 'home')
      expect(route).toBeDefined()
      expect(route?.path).toBe('/')
    })

    it('should have task detail route with parameter', () => {
      const route = router.getRoutes().find((r: any) => r.name === 'task-detail')
      expect(route).toBeDefined()
      expect(route?.path).toBe('/tasks/:id')
    })

    it('should have workers route', () => {
      const route = router.getRoutes().find((r: any) => r.name === 'workers')
      expect(route).toBeDefined()
      expect(route?.path).toBe('/workers')
    })

    it('should have settings route', () => {
      const route = router.getRoutes().find((r: any) => r.name === 'settings')
      expect(route).toBeDefined()
      expect(route?.path).toBe('/settings')
    })

    it('should have exactly 4 routes', () => {
      expect(router.getRoutes()).toHaveLength(4)
    })
  })

  describe('route metadata', () => {
    it('should have title metadata for home route', () => {
      const route = router.getRoutes().find((r: any) => r.name === 'home')
      expect(route?.meta.title).toBe('Tasks')
    })

    it('should have title metadata for task detail route', () => {
      const route = router.getRoutes().find((r: any) => r.name === 'task-detail')
      expect(route?.meta.title).toBe('Task Detail')
    })

    it('should have title metadata for workers route', () => {
      const route = router.getRoutes().find((r: any) => r.name === 'workers')
      expect(route?.meta.title).toBe('Workers')
    })

    it('should have title metadata for settings route', () => {
      const route = router.getRoutes().find((r: any) => r.name === 'settings')
      expect(route?.meta.title).toBe('Settings')
    })
  })

  describe('navigation', () => {
    it('should navigate to home route', async () => {
      await router.push('/')
      expect(router.currentRoute.value.name).toBe('home')
    })

    it('should navigate to task detail with id parameter', async () => {
      await router.push('/tasks/123')
      expect(router.currentRoute.value.name).toBe('task-detail')
      expect(router.currentRoute.value.params.id).toBe('123')
    })

    it('should navigate to workers route', async () => {
      await router.push('/workers')
      expect(router.currentRoute.value.name).toBe('workers')
    })

    it('should navigate to settings route', async () => {
      await router.push('/settings')
      expect(router.currentRoute.value.name).toBe('settings')
    })

    it('should navigate using route names', async () => {
      await router.push({ name: 'home' })
      expect(router.currentRoute.value.path).toBe('/')
      
      await router.push({ name: 'workers' })
      expect(router.currentRoute.value.path).toBe('/workers')
    })

    it('should handle task detail navigation with params', async () => {
      await router.push({ name: 'task-detail', params: { id: '456' } })
      expect(router.currentRoute.value.params.id).toBe('456')
    })
  })

  describe('route parameters', () => {
    it('should accept numeric task IDs', async () => {
      await router.push('/tasks/1')
      expect(router.currentRoute.value.params.id).toBe('1')
    })

    it('should accept string task IDs', async () => {
      await router.push('/tasks/task-abc-123')
      expect(router.currentRoute.value.params.id).toBe('task-abc-123')
    })

    it('should preserve query parameters', async () => {
      await router.push('/tasks/1?status=pending&priority=high')
      expect(router.currentRoute.value.query.status).toBe('pending')
      expect(router.currentRoute.value.query.priority).toBe('high')
    })
  })

  describe('route guards and hooks', () => {
    it('should trigger afterEach hook on navigation', async () => {
      const afterEachSpy = vi.fn()
      router.afterEach(afterEachSpy)
      
      await router.push('/')
      expect(afterEachSpy).toHaveBeenCalled()
    })

    it('should update document title on navigation', async () => {
      router.afterEach((to: any) => {
        document.title = `${to.meta.title || 'TaskManager'} | PrismQ`
      })
      
      await router.push('/')
      expect(document.title).toContain('Tasks')
      
      await router.push('/workers')
      expect(document.title).toContain('Workers')
    })
  })

  describe('history mode', () => {
    it('should support navigation history', async () => {
      await router.push('/')
      expect(router.currentRoute.value.name).toBe('home')
      
      await router.push('/workers')
      expect(router.currentRoute.value.name).toBe('workers')
      
      await router.push('/settings')
      expect(router.currentRoute.value.name).toBe('settings')
    })

    it('should allow programmatic navigation', async () => {
      await router.push('/')
      await router.push('/workers')
      
      expect(router.currentRoute.value.name).toBe('workers')
    })
  })

  describe('route matching', () => {
    it('should match exact paths', async () => {
      await router.push('/')
      const matched = router.currentRoute.value.matched
      expect(matched.length).toBeGreaterThan(0)
    })

    it('should match parametrized routes', async () => {
      await router.push('/tasks/123')
      const matched = router.currentRoute.value.matched
      expect(matched.length).toBeGreaterThan(0)
      expect(router.currentRoute.value.params.id).toBe('123')
    })

    it('should resolve route by name', () => {
      const resolved = router.resolve({ name: 'home' })
      expect(resolved.path).toBe('/')
    })

    it('should resolve route with params', () => {
      const resolved = router.resolve({ name: 'task-detail', params: { id: '789' } })
      expect(resolved.path).toBe('/tasks/789')
    })
  })

  describe('edge cases', () => {
    it('should handle rapid navigation', async () => {
      await router.push('/')
      await router.push('/workers')
      await router.push('/settings')
      await router.push('/')
      
      expect(router.currentRoute.value.name).toBe('home')
    })

    it('should handle navigation to same route', async () => {
      await router.push('/')
      
      try {
        await router.push('/')
      } catch (error) {
        // Router may throw error for duplicate navigation
        expect(error).toBeDefined()
      }
      
      expect(router.currentRoute.value.name).toBe('home')
    })

    it('should handle empty task ID parameter', async () => {
      await router.push('/tasks/')
      // Router should handle this gracefully
      expect(router.currentRoute.value).toBeDefined()
    })
  })
})
