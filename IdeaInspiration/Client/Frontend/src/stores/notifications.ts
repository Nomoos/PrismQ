/**
 * Notification store for managing toast notifications.
 * 
 * This store follows SOLID principles:
 * - Single Responsibility: Manages notification state only
 * - Interface Segregation: Provides focused methods for different notification types
 * - Dependency Inversion: Can be used by any component without tight coupling
 */

import { defineStore } from 'pinia'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  errorCode?: string
  duration?: number
}

export const useNotificationStore = defineStore('notifications', {
  state: () => ({
    notifications: [] as Notification[],
  }),

  actions: {
    /**
     * Add a notification to the store.
     * 
     * @param notification - Notification to add (without ID)
     */
    add(notification: Omit<Notification, 'id'>) {
      const id = `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`
      const duration = notification.duration ?? (notification.type === 'error' ? 10000 : 5000)

      this.notifications.push({ ...notification, id, duration })

      // Auto-remove after duration
      if (duration > 0) {
        setTimeout(() => this.remove(id), duration)
      }
    },

    /**
     * Add a success notification.
     * 
     * @param options - Notification options
     */
    success(options: Omit<Notification, 'id' | 'type'>) {
      this.add({ ...options, type: 'success' })
    },

    /**
     * Add an error notification.
     * 
     * @param options - Notification options
     */
    error(options: Omit<Notification, 'id' | 'type'>) {
      this.add({ ...options, type: 'error' })
    },

    /**
     * Add a warning notification.
     * 
     * @param options - Notification options
     */
    warning(options: Omit<Notification, 'id' | 'type'>) {
      this.add({ ...options, type: 'warning' })
    },

    /**
     * Add an info notification.
     * 
     * @param options - Notification options
     */
    info(options: Omit<Notification, 'id' | 'type'>) {
      this.add({ ...options, type: 'info' })
    },

    /**
     * Remove a notification by ID.
     * 
     * @param id - Notification ID to remove
     */
    remove(id: string) {
      const index = this.notifications.findIndex((n) => n.id === id)
      if (index !== -1) {
        this.notifications.splice(index, 1)
      }
    },

    /**
     * Clear all notifications.
     */
    clear() {
      this.notifications = []
    },
  },
})
