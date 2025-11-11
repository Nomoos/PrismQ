<template>
  <span
    role="status"
    :aria-label="`Status: ${props.status}`"
    :class="[
      'inline-block px-2 py-1 rounded text-xs font-medium',
      badgeClasses
    ]"
  >
    {{ displayText }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  status: string
  uppercase?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  uppercase: true
})

const badgeClasses = computed(() => {
  const classes: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800 dark:bg-dark-warning-subtle dark:text-dark-warning-text dark:border dark:border-dark-warning-border',
    claimed: 'bg-blue-100 text-blue-800 dark:bg-dark-info-subtle dark:text-dark-info-text dark:border dark:border-dark-info-border',
    completed: 'bg-green-100 text-green-800 dark:bg-dark-success-subtle dark:text-dark-success-text dark:border dark:border-dark-success-border',
    failed: 'bg-red-100 text-red-800 dark:bg-dark-error-subtle dark:text-dark-error-text dark:border dark:border-dark-error-border',
    active: 'bg-green-100 text-green-800 dark:bg-dark-success-subtle dark:text-dark-success-text dark:border dark:border-dark-success-border',
    idle: 'bg-yellow-100 text-yellow-800 dark:bg-dark-warning-subtle dark:text-dark-warning-text dark:border dark:border-dark-warning-border',
    offline: 'bg-gray-100 text-gray-800 dark:bg-dark-neutral-subtle dark:text-dark-neutral-text dark:border dark:border-dark-neutral-border'
  }
  return classes[props.status.toLowerCase()] || 'bg-gray-100 text-gray-800 dark:bg-dark-neutral-subtle dark:text-dark-neutral-text dark:border dark:border-dark-neutral-border'
})

const displayText = computed(() => {
  return props.uppercase ? props.status.toUpperCase() : props.status
})
</script>
