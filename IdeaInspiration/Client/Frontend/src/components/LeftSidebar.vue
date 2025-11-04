<template>
  <div class="left-sidebar">
    <div class="sidebar-header">
      <h3 class="sidebar-title">Quick Filters</h3>
    </div>
    
    <div class="sidebar-content">
      <!-- All Modules -->
      <button
        @click="$emit('filter-change', 'all')"
        :class="['filter-button', { active: currentFilter === 'all' }]"
      >
        <span class="filter-icon">📋</span>
        <span class="filter-label">All Modules</span>
        <span class="filter-count">{{ totalModules }}</span>
      </button>

      <!-- Most Used -->
      <button
        @click="$emit('filter-change', 'most-used')"
        :class="['filter-button', { active: currentFilter === 'most-used' }]"
      >
        <span class="filter-icon">🔥</span>
        <span class="filter-label">Most Used</span>
        <span class="filter-count">{{ mostUsedCount }}</span>
      </button>

      <!-- Most Recent -->
      <button
        @click="$emit('filter-change', 'recent')"
        :class="['filter-button', { active: currentFilter === 'recent' }]"
      >
        <span class="filter-icon">🕐</span>
        <span class="filter-label">Recently Used</span>
        <span class="filter-count">{{ recentCount }}</span>
      </button>

      <!-- Divider -->
      <div class="sidebar-divider"></div>

      <!-- Categories -->
      <div class="sidebar-section">
        <h4 class="section-title">Categories</h4>
        <button
          v-for="category in categories"
          :key="category.name"
          @click="$emit('filter-change', 'category', category.name)"
          :class="['filter-button', 'category-button', { 
            active: currentFilter === 'category' && selectedCategory === category.name 
          }]"
        >
          <span class="filter-label">{{ category.name }}</span>
          <span class="filter-count">{{ category.count }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

interface Category {
  name: string
  count: number
}

defineProps<{
  currentFilter: string
  selectedCategory?: string
  totalModules: number
  mostUsedCount: number
  recentCount: number
  categories: Category[]
}>()

defineEmits<{
  (e: 'filter-change', filter: string, category?: string): void
}>()
</script>

<style scoped>
.left-sidebar {
  @apply w-64 bg-white border-r border-gray-200 flex-shrink-0;
}

.sidebar-header {
  @apply p-4 border-b border-gray-200;
}

.sidebar-title {
  @apply text-lg font-semibold text-gray-900;
}

.sidebar-content {
  @apply p-3 space-y-1;
}

.filter-button {
  @apply w-full flex items-center justify-between px-3 py-2 text-sm text-gray-700
         rounded-md hover:bg-gray-100 transition-colors duration-150;
}

.filter-button.active {
  @apply bg-blue-50 text-blue-700 font-medium;
}

.filter-button .filter-icon {
  @apply text-lg mr-2;
}

.filter-button .filter-label {
  @apply flex-1 text-left;
}

.filter-button .filter-count {
  @apply text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full;
}

.filter-button.active .filter-count {
  @apply bg-blue-100 text-blue-700;
}

.sidebar-divider {
  @apply my-4 border-t border-gray-200;
}

.sidebar-section {
  @apply space-y-1;
}

.section-title {
  @apply text-xs font-semibold text-gray-500 uppercase tracking-wider px-3 py-2;
}

.category-button {
  @apply pl-6;
}
</style>
