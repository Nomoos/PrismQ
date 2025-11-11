import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/TaskList.vue'),
    meta: { title: 'Tasks' }
  },
  {
    path: '/tasks/new',
    name: 'task-create',
    component: () => import('../views/TaskCreate.vue'),
    meta: { title: 'Create Task' }
  },
  {
    path: '/tasks/:id',
    name: 'task-detail',
    component: () => import('../views/TaskDetail.vue'),
    meta: { title: 'Task Detail' }
  },
  {
    path: '/workers',
    name: 'workers',
    component: () => import('../views/WorkerDashboard.vue'),
    meta: { title: 'Workers' }
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../views/Settings.vue'),
    meta: { title: 'Settings' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.afterEach((to) => {
  document.title = `${to.meta.title || 'TaskManager'} | PrismQ`
})

export default router
