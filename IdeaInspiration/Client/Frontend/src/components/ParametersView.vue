<template>
  <div class="parameters-view">
    <h3 class="text-lg font-semibold mb-4">Run Parameters</h3>
    
    <div v-if="parameters && Object.keys(parameters).length > 0" class="parameter-list">
      <div 
        v-for="(value, key) in parameters" 
        :key="key"
        class="parameter-item"
      >
        <span class="parameter-key">{{ key }}</span>
        <span class="parameter-value">{{ formatValue(value) }}</span>
      </div>
    </div>
    
    <div v-else class="empty-state">
      No parameters specified for this run.
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  parameters: Record<string, any>
}>()

function formatValue(value: any): string {
  if (value === null || value === undefined) {
    return 'null'
  }
  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2)
  }
  return String(value)
}
</script>

<style scoped>
.parameters-view {
  @apply bg-white rounded-lg border border-gray-200 p-6;
}

.parameter-list {
  @apply space-y-3;
}

.parameter-item {
  @apply flex justify-between items-start p-3 bg-gray-50 rounded border border-gray-200;
}

.parameter-key {
  @apply font-medium text-gray-700 mr-4;
}

.parameter-value {
  @apply text-gray-900 font-mono text-sm break-all;
}

.empty-state {
  @apply text-center py-8 text-gray-500;
}
</style>
