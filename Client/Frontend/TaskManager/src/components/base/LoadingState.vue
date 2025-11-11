<template>
  <div 
    :class="['text-center', paddingClass]" 
    role="status" 
    aria-live="polite"
  >
    <LoadingSpinner :size="size" />
    <p 
      v-if="message" 
      class="mt-2 text-gray-600 dark:text-dark-text-secondary"
    >
      {{ message }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import LoadingSpinner from './LoadingSpinner.vue'

const props = withDefaults(defineProps<{
  message?: string
  size?: 'sm' | 'md' | 'lg'
  padding?: 'sm' | 'md' | 'lg'
}>(), {
  message: 'Loading...',
  size: 'lg',
  padding: 'lg'
})

const paddingClass = computed(() => {
  switch (props.padding) {
    case 'sm':
      return 'py-4'
    case 'md':
      return 'py-6'
    case 'lg':
    default:
      return 'py-8'
  }
})
</script>

