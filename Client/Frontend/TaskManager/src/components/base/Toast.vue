<template>
  <Transition name="toast">
    <div
      v-if="visible"
      :class="[
        'fixed bottom-20 left-4 right-4 z-50 p-4 rounded-lg shadow-lg',
        'flex items-center gap-3 text-white font-medium',
        typeClasses
      ]"
      role="alert"
      @click="close"
    >
      <div class="flex-shrink-0">
        <svg v-if="type === 'success'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <svg v-else-if="type === 'error'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        <svg v-else-if="type === 'warning'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div class="flex-1">
        {{ message }}
      </div>
      <button
        @click.stop="close"
        class="flex-shrink-0 p-1 hover:opacity-80 focus:outline-none min-w-[44px] min-h-[44px] flex items-center justify-center"
        aria-label="Close notification"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'

export interface ToastProps {
  message: string
  type?: 'success' | 'error' | 'warning' | 'info'
  duration?: number
  visible?: boolean
}

const props = withDefaults(defineProps<ToastProps>(), {
  type: 'info',
  duration: 3000,
  visible: true
})

const emit = defineEmits<{
  close: []
}>()

const visible = ref(props.visible)

const typeClasses = computed(() => {
  const classes = {
    success: 'bg-green-600 dark:bg-dark-success-bg',
    error: 'bg-red-600 dark:bg-dark-error-bg',
    warning: 'bg-yellow-600 dark:bg-dark-warning-bg',
    info: 'bg-blue-600 dark:bg-dark-info-bg'
  }
  return classes[props.type]
})

let timeoutId: ReturnType<typeof setTimeout> | null = null

function close() {
  visible.value = false
  if (timeoutId) {
    clearTimeout(timeoutId)
  }
  emit('close')
}

watch(() => props.visible, (newVal) => {
  visible.value = newVal
})

onMounted(() => {
  if (props.duration > 0) {
    timeoutId = setTimeout(() => {
      close()
    }, props.duration)
  }
})
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
