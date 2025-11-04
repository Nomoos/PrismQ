<template>
  <div class="module-tabs">
    <div class="tabs-container">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="$emit('tab-change', tab.id)"
        :class="['tab-button', { active: currentTab === tab.id }]"
      >
        <span class="tab-icon" v-if="tab.icon">{{ tab.icon }}</span>
        <span class="tab-label">{{ tab.label }}</span>
        <span class="tab-count" v-if="tab.count !== undefined">({{ tab.count }})</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

interface Tab {
  id: string
  label: string
  icon?: string
  count?: number
}

defineProps<{
  tabs: Tab[]
  currentTab: string
}>()

defineEmits<{
  (e: 'tab-change', tabId: string): void
}>()
</script>

<style scoped>
.module-tabs {
  @apply mb-6;
}

.tabs-container {
  @apply flex gap-2 border-b border-gray-200 overflow-x-auto;
}

.tab-button {
  @apply flex items-center gap-2 px-4 py-3 text-sm font-medium text-gray-600 
         border-b-2 border-transparent transition-all duration-200
         hover:text-gray-900 hover:border-gray-300 whitespace-nowrap;
}

.tab-button.active {
  @apply text-blue-600 border-blue-600;
}

.tab-icon {
  @apply text-lg;
}

.tab-label {
  @apply font-medium;
}

.tab-count {
  @apply text-xs text-gray-500;
}
</style>
