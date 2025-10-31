<template>
  <div class="module-card">
    <div class="module-header">
      <h3 class="module-title">{{ module.name }}</h3>
      <span class="category-badge">{{ module.category }}</span>
    </div>
    
    <p class="description">{{ module.description }}</p>
    
    <!-- Stats -->
    <div class="module-stats" v-if="module.total_runs !== undefined">
      <span class="stat">{{ module.total_runs }} runs</span>
      <span class="stat" v-if="module.success_rate !== undefined">{{ module.success_rate }}% success</span>
    </div>
    
    <!-- Tags -->
    <div class="module-tags" v-if="module.tags && module.tags.length > 0">
      <span v-for="tag in module.tags" :key="tag" class="tag">
        {{ tag }}
      </span>
    </div>

    <!-- Status indicator -->
    <div class="status-row">
      <span class="status-badge" :class="statusClass">
        {{ module.status || 'active' }}
      </span>
      <span class="version-badge" v-if="module.version">v{{ module.version }}</span>
    </div>

    <button
      @click="handleLaunch"
      :disabled="!module.enabled || module.status === 'maintenance'"
      class="launch-button"
      :class="{ 'cursor-not-allowed': !module.enabled || module.status === 'maintenance' }"
    >
      {{ buttonText }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Module } from '@/types/module'

const props = defineProps<{
  module: Module
}>()

const emit = defineEmits<{
  launch: [module: Module]
}>()

const buttonText = computed(() => {
  if (!props.module.enabled) return 'Disabled'
  if (props.module.status === 'maintenance') return 'Maintenance'
  return 'Launch Module'
})

const statusClass = computed(() => {
  const status = props.module.status || 'active'
  return {
    'status-active': status === 'active',
    'status-inactive': status === 'inactive',
    'status-maintenance': status === 'maintenance'
  }
})

function handleLaunch() {
  emit('launch', props.module)
}
</script>

<style scoped>
.module-card {
  @apply bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow border border-gray-200;
}

.module-header {
  @apply flex justify-between items-start mb-3;
}

.module-title {
  @apply text-xl font-semibold text-gray-900;
}

.category-badge {
  @apply px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm whitespace-nowrap;
}

.description {
  @apply text-gray-700 mb-4 line-clamp-3;
}

.module-stats {
  @apply flex gap-3 mb-3 text-sm text-gray-600;
}

.stat {
  @apply flex items-center gap-1;
}

.module-tags {
  @apply flex flex-wrap gap-2 mb-4;
}

.tag {
  @apply px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs;
}

.status-row {
  @apply flex items-center gap-2 mb-4;
}

.status-badge {
  @apply px-2 py-1 rounded-full text-xs font-medium;
}

.status-active {
  @apply bg-green-100 text-green-800;
}

.status-inactive {
  @apply bg-gray-100 text-gray-800;
}

.status-maintenance {
  @apply bg-yellow-100 text-yellow-800;
}

.version-badge {
  @apply text-xs text-gray-500;
}

.launch-button {
  @apply w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded transition-colors;
}
</style>
