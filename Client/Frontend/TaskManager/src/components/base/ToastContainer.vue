<template>
  <Teleport to="body">
    <div class="fixed inset-0 pointer-events-none z-50">
      <div class="flex flex-col gap-2 items-stretch p-4 pb-20">
        <TransitionGroup name="toast-list">
          <div
            v-for="toast in toasts"
            :key="toast.id"
            :class="[
              'pointer-events-auto p-4 rounded-lg shadow-lg',
              'flex items-center gap-3 text-white font-medium',
              'min-h-[44px]',
              typeClasses[toast.type]
            ]"
            role="alert"
            @click="removeToast(toast.id)"
          >
            <div class="flex-shrink-0">
              <svg v-if="toast.type === 'success'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else-if="toast.type === 'error'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              <svg v-else-if="toast.type === 'warning'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="flex-1 text-sm">
              {{ toast.message }}
            </div>
            <button
              @click.stop="removeToast(toast.id)"
              class="flex-shrink-0 p-1 hover:opacity-80 focus:outline-none min-w-[44px] min-h-[44px] flex items-center justify-center"
              aria-label="Close notification"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </TransitionGroup>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useToast } from '../../composables/useToast'

const { toasts, removeToast } = useToast()

const typeClasses: Record<string, string> = {
  success: 'bg-green-600',
  error: 'bg-red-600',
  warning: 'bg-yellow-600',
  info: 'bg-blue-600'
}
</script>

<style scoped>
.toast-list-enter-active,
.toast-list-leave-active {
  transition: all 0.3s ease;
}

.toast-list-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-list-leave-to {
  opacity: 0;
  transform: translateX(-100%);
}

.toast-list-move {
  transition: transform 0.3s ease;
}
</style>
