<template>
  <div class="stat-card">
    <div class="stat-label">{{ label }}</div>
    <div class="stat-value">{{ value }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
}>()
</script>

<style scoped>
.stat-card {
  @apply bg-white border border-gray-200 rounded-lg p-4;
}

.stat-label {
  @apply text-sm font-medium text-gray-600 mb-1;
}

.stat-value {
  @apply text-2xl font-semibold text-gray-900;
}
</style>
