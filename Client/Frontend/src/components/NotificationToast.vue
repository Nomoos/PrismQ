<template>
  <teleport to="body">
    <div class="notification-container">
      <TransitionGroup name="slide-fade">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          :class="['notification', `notification-${notification.type}`]"
        >
          <div class="notification-icon">
            {{ getIcon(notification.type) }}
          </div>

          <div class="notification-content">
            <h4 class="notification-title">{{ notification.title }}</h4>
            <p class="notification-message">{{ notification.message }}</p>
            <small v-if="notification.errorCode" class="notification-code">
              Code: {{ notification.errorCode }}
            </small>
          </div>

          <button
            @click="store.remove(notification.id)"
            class="notification-close"
            aria-label="Close notification"
          >
            ×
          </button>
        </div>
      </TransitionGroup>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useNotificationStore } from '@/stores/notifications'

const store = useNotificationStore()
const { notifications } = storeToRefs(store)

/**
 * Get icon for notification type.
 * 
 * @param type - Notification type
 * @returns Icon string
 */
function getIcon(type: string): string {
  const icons: Record<string, string> = {
    success: '✓',
    error: '✗',
    warning: '⚠',
    info: 'ℹ',
  }
  return icons[type] || '•'
}
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 400px;
  pointer-events: none;
}

.notification {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  background: white;
  pointer-events: auto;
  min-width: 300px;
}

.notification-icon {
  font-size: 1.5rem;
  font-weight: bold;
  line-height: 1;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #1f2937;
}

.notification-message {
  margin: 0;
  font-size: 0.875rem;
  color: #4b5563;
  word-wrap: break-word;
}

.notification-code {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
  font-family: monospace;
}

.notification-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: #9ca3af;
  padding: 0;
  width: 1.5rem;
  height: 1.5rem;
  flex-shrink: 0;
  transition: color 0.2s;
}

.notification-close:hover {
  color: #4b5563;
}

.notification-success {
  border-left: 4px solid #10b981;
}

.notification-success .notification-icon {
  color: #10b981;
}

.notification-error {
  border-left: 4px solid #ef4444;
}

.notification-error .notification-icon {
  color: #ef4444;
}

.notification-warning {
  border-left: 4px solid #f59e0b;
}

.notification-warning .notification-icon {
  color: #f59e0b;
}

.notification-info {
  border-left: 4px solid #3b82f6;
}

.notification-info .notification-icon {
  color: #3b82f6;
}

/* Animations */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.slide-fade-move {
  transition: transform 0.3s ease;
}
</style>
