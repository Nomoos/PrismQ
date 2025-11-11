<template>
  <div 
    class="bg-red-50 dark:bg-dark-error-subtle border border-red-200 dark:border-dark-error-border rounded-lg p-4"
    role="alert"
    aria-live="assertive"
  >
    <p class="text-red-800 dark:text-dark-error-text">{{ message }}</p>
    <button 
      v-if="retryable" 
      @click="$emit('retry')" 
      class="btn-primary mt-2"
      :aria-label="retryLabel"
    >
      {{ retryLabel }}
    </button>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  message: string
  retryable?: boolean
  retryLabel?: string
}>(), {
  retryable: true,
  retryLabel: 'Retry'
})

defineEmits<{
  retry: []
}>()
</script>
