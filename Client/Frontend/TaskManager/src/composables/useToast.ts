import { ref } from 'vue'

export interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
  duration: number
}

const toasts = ref<Toast[]>([])
let nextId = 1

export function useToast() {
  function showToast(
    message: string,
    type: 'success' | 'error' | 'warning' | 'info' = 'info',
    duration = 3000
  ) {
    const id = nextId++
    const toast: Toast = {
      id,
      message,
      type,
      duration
    }

    toasts.value.push(toast)

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }

    return id
  }

  function removeToast(id: number) {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  function success(message: string, duration = 3000) {
    return showToast(message, 'success', duration)
  }

  function error(message: string, duration = 4000) {
    return showToast(message, 'error', duration)
  }

  function warning(message: string, duration = 3500) {
    return showToast(message, 'warning', duration)
  }

  function info(message: string, duration = 3000) {
    return showToast(message, 'info', duration)
  }

  function clear() {
    toasts.value = []
  }

  return {
    toasts,
    showToast,
    removeToast,
    success,
    error,
    warning,
    info,
    clear
  }
}
