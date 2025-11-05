<template>
  <!-- Category/Node Button -->
  <button
    @click="handleClick"
    :class="['filter-button', `level-${level}`, { 
      active: currentFilter === 'category' && selectedCategory === node.fullName 
    }]"
    :style="{ paddingLeft: `${0.75 + level * 1}rem` }"
  >
    <span class="expand-icon" v-if="node.children.length > 0">
      {{ isExpanded ? '▼' : '▶' }}
    </span>
    <span class="expand-icon" v-else>•</span>
    <span class="filter-label">{{ node.name }}</span>
    <span class="filter-count">{{ node.count }}</span>
  </button>

  <!-- Children (when expanded) -->
  <template v-if="isExpanded && node.children.length > 0">
    <CategoryTreeNode
      v-for="child in node.children"
      :key="child.fullName"
      :node="child"
      :level="level + 1"
      :expanded-categories="expandedCategories"
      :current-filter="currentFilter"
      :selected-category="selectedCategory"
      @toggle="$emit('toggle', $event)"
      @select="$emit('select', $event)"
    />
  </template>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CategoryTreeNode } from '@/types/category'

const props = defineProps<{
  node: CategoryTreeNode
  level: number
  expandedCategories: Set<string>
  currentFilter: string
  selectedCategory?: string
}>()

const emit = defineEmits<{
  (e: 'toggle', fullName: string): void
  (e: 'select', fullName: string): void
}>()

const isExpanded = computed(() => props.expandedCategories.has(props.node.fullName))

function handleClick() {
  if (props.node.children.length > 0) {
    // Has children - toggle expansion
    emit('toggle', props.node.fullName)
  } else {
    // Leaf node - select for filtering
    emit('select', props.node.fullName)
  }
}
</script>

<script lang="ts">
// Enable recursive component
export default {
  name: 'CategoryTreeNode'
}
</script>

<style scoped>
.filter-button {
  @apply w-full flex items-center justify-between py-2 text-sm text-gray-700
         rounded-md hover:bg-gray-100 transition-colors duration-150 cursor-pointer;
}

.filter-button.active {
  @apply bg-blue-50 text-blue-700 font-medium;
}

.filter-button .expand-icon {
  @apply text-xs mr-2 text-gray-400 w-3 inline-block flex-shrink-0;
}

.filter-button .filter-label {
  @apply flex-1 text-left;
}

.filter-button .filter-count {
  @apply text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full flex-shrink-0;
}

.filter-button.active .filter-count {
  @apply bg-blue-100 text-blue-700;
}
</style>
