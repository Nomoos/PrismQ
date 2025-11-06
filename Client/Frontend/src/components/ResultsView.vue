<template>
  <div class="results-view">
    <h3 class="text-lg font-semibold mb-4">Run Results</h3>
    
    <div v-if="loading" class="loading-state">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="mt-2 text-gray-600">Loading results...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p class="text-red-600">{{ error }}</p>
    </div>
    
    <div v-else class="results-content">
      <p class="text-gray-600">
        Results will be displayed here when the backend provides result endpoints.
      </p>
      <p class="text-sm text-gray-500 mt-2">
        Run ID: {{ runId }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  runId: string
}>()

const loading = ref(false)
const error = ref<string | null>(null)

// Placeholder for future implementation
// In a real implementation, this would fetch results from an API
</script>

<style scoped>
.results-view {
  @apply bg-white rounded-lg border border-gray-200 p-6;
}

.loading-state {
  @apply text-center py-12;
}

.error-state {
  @apply bg-red-50 border border-red-200 p-4 rounded;
}

.results-content {
  @apply text-center py-8;
}
</style>
