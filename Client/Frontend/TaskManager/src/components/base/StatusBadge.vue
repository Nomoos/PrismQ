<template>
  <span
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
    pending: 'bg-yellow-100 text-yellow-800',
    claimed: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    active: 'bg-green-100 text-green-800',
    idle: 'bg-yellow-100 text-yellow-800',
    offline: 'bg-gray-100 text-gray-800'
  }
  return classes[props.status.toLowerCase()] || 'bg-gray-100 text-gray-800'
})

const displayText = computed(() => {
  return props.uppercase ? props.status.toUpperCase() : props.status
})
</script>
