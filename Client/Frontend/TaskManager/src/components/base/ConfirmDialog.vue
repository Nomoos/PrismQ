<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
        @click.self="handleCancel"
      >
        <div
          class="bg-white rounded-lg shadow-xl max-w-md w-full p-6 animate-fade-in"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="`modal-title-${uniqueId}`"
        >
          <h2 :id="`modal-title-${uniqueId}`" class="text-xl font-bold text-gray-900 mb-4">
            {{ title }}
          </h2>
          
          <p class="text-gray-700 mb-6">
            {{ message }}
          </p>
          
          <div class="flex gap-3 justify-end">
            <button
              @click="handleCancel"
              class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-medium hover:bg-gray-300 min-h-[44px] min-w-[80px]"
            >
              {{ cancelText }}
            </button>
            <button
              @click="handleConfirm"
              :class="[
                'px-4 py-2 rounded-lg font-medium min-h-[44px] min-w-[80px]',
                dangerMode
                  ? 'bg-red-600 text-white hover:bg-red-700'
                  : 'bg-primary-600 text-white hover:bg-primary-700'
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
import { computed } from 'vue'

export interface ConfirmDialogProps {
  modelValue: boolean
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
  dangerMode?: boolean
}

withDefaults(defineProps<ConfirmDialogProps>(), {
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

function handleConfirm() {
  emit('confirm')
  emit('update:modelValue', false)
}

function handleCancel() {
  emit('cancel')
  emit('update:modelValue', false)
}
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
