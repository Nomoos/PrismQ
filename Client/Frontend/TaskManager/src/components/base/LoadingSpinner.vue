<template>
  <div
    :class="[
      'inline-block animate-spin rounded-full border-t-transparent',
      sizeClasses,
      colorClasses
    ]"
    role="status"
    :aria-label="label"
  >
    <span class="sr-only">{{ label }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'sm' | 'md' | 'lg'
  color?: 'primary' | 'white' | 'gray'
  label?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  color: 'primary',
  label: 'Loading...'
})

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-4',
    lg: 'h-12 w-12 border-4'
  }
  return sizes[props.size]
})

const colorClasses = computed(() => {
  const colors = {
    primary: 'border-primary-500 dark:border-dark-primary-text',
    white: 'border-white',
    gray: 'border-gray-500 dark:border-dark-text-secondary'
  }
  return colors[props.color]
})
</script>

<style scoped>
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
