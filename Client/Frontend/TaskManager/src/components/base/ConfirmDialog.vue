<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 dark:bg-opacity-70"
        @click.self="handleCancel"
      >
        <div
          ref="dialogRef"
          class="bg-white dark:bg-dark-surface-default rounded-lg shadow-xl max-w-md w-full p-6 animate-fade-in dark:border dark:border-dark-border-default"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="`modal-title-${uniqueId}`"
          :aria-describedby="`modal-desc-${uniqueId}`"
        >
          <h2 :id="`modal-title-${uniqueId}`" class="text-xl font-bold text-gray-900 dark:text-dark-text-primary mb-4">
            {{ title }}
          </h2>
          
          <p :id="`modal-desc-${uniqueId}`" class="text-gray-700 dark:text-dark-text-secondary mb-6">
            {{ message }}
          </p>
          
          <div class="flex gap-3 justify-end">
            <button
              @click="handleCancel"
              aria-label="Cancel action"
              class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-medium hover:bg-gray-300 min-h-[44px] min-w-[80px] dark:bg-dark-neutral-bg dark:text-dark-text-primary dark:hover:bg-dark-border-default"
            >
              {{ cancelText }}
            </button>
            <button
              @click="handleConfirm"
              :aria-label="dangerMode ? 'Confirm dangerous action' : 'Confirm action'"
              :class="[
                'px-4 py-2 rounded-lg font-medium min-h-[44px] min-w-[80px]',
                dangerMode
                  ? 'bg-red-600 text-white hover:bg-red-700 dark:bg-dark-error-bg dark:hover:bg-dark-error-muted'
                  : 'bg-primary-600 text-white hover:bg-primary-700 dark:bg-dark-primary-bg dark:hover:bg-dark-primary-hover'
              ]"
            >
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, watch, onMounted, onUnmounted, ref } from 'vue'

export interface ConfirmDialogProps {
  modelValue: boolean
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
  dangerMode?: boolean
}

const props = withDefaults(defineProps<ConfirmDialogProps>(), {
  title: 'Confirm Action',
  message: 'Are you sure you want to continue?',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  dangerMode: false
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: []
  cancel: []
}>()

let idCounter = 0
const uniqueId = computed(() => `dialog-${++idCounter}`)
const dialogRef = ref<HTMLElement | null>(null)
const previousActiveElement = ref<HTMLElement | null>(null)

function handleConfirm() {
  emit('confirm')
  emit('update:modelValue', false)
}

function handleCancel() {
  emit('cancel')
  emit('update:modelValue', false)
}

function handleEscape(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.modelValue) {
    handleCancel()
  }
}

// Focus trap implementation
function trapFocus(e: KeyboardEvent) {
  if (!props.modelValue || !dialogRef.value || e.key !== 'Tab') return

  const focusableElements = dialogRef.value.querySelectorAll<HTMLElement>(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )
  
  const firstElement = focusableElements[0]
  const lastElement = focusableElements[focusableElements.length - 1]

  if (e.shiftKey) {
    // Shift + Tab: going backwards
    if (document.activeElement === firstElement) {
      e.preventDefault()
      lastElement?.focus()
    }
  } else {
    // Tab: going forwards
    if (document.activeElement === lastElement) {
      e.preventDefault()
      firstElement?.focus()
    }
  }
}

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    // Store the element that had focus before opening the dialog
    previousActiveElement.value = document.activeElement as HTMLElement
    
    // Focus the first focusable element in the dialog
    setTimeout(() => {
      const firstButton = dialogRef.value?.querySelector('button')
      firstButton?.focus()
    }, 100)
  } else {
    // Restore focus to the element that had focus before opening
    if (previousActiveElement.value) {
      previousActiveElement.value.focus()
    }
  }
})

onMounted(() => {
  document.addEventListener('keydown', handleEscape)
  document.addEventListener('keydown', trapFocus)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
  document.removeEventListener('keydown', trapFocus)
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .bg-white,
.modal-leave-active .bg-white {
  transition: transform 0.3s ease;
}

.modal-enter-from .bg-white {
  transform: scale(0.9) translateY(20px);
}

.modal-leave-to .bg-white {
  transform: scale(0.9) translateY(-20px);
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease;
}
</style>
