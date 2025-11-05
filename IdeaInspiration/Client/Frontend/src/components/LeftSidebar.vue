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

      <!-- Categories Tree -->
      <div class="sidebar-section">
        <h4 class="section-title">Categories</h4>
        <CategoryTreeNode
          v-for="category in categoryTree"
          :key="category.fullName"
          :node="category"
          :level="0"
          :expanded-categories="expandedCategories"
          :current-filter="currentFilter"
          :selected-category="selectedCategory"
          @toggle="toggleCategory"
          @select="(fullName) => $emit('filter-change', 'category', fullName)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import CategoryTreeNode from './CategoryTreeNode.vue'
import type { CategoryTreeNode as CategoryTreeNodeType } from '@/types/category'

interface Category {
  name: string
  count: number
}

const props = defineProps<{
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
const expandedCategories = ref<Set<string>>(new Set())

// Build hierarchical tree from flat category list (supports multi-level nesting)
const categoryTree = computed(() => {
  const root: CategoryTreeNodeType[] = []
  const nodeMap = new Map<string, CategoryTreeNodeType>()

  // Sort categories to ensure proper hierarchy
  const sortedCategories = [...props.categories].sort((a, b) => 
    a.name.localeCompare(b.name)
  )

  // Helper function to get or create node at path
  function getOrCreateNode(path: string[]): CategoryTreeNodeType {
    const fullPath = path.join('/')
    
    if (nodeMap.has(fullPath)) {
      return nodeMap.get(fullPath)!
    }
    
    const name = path[path.length - 1]
    const node: CategoryTreeNodeType = {
      name,
      fullName: fullPath,
      count: 0,
      children: []
    }
    
    nodeMap.set(fullPath, node)
    
    if (path.length === 1) {
      // Top-level node
      root.push(node)
    } else {
      // Nested node - add to parent
      const parentPath = path.slice(0, -1)
      const parent = getOrCreateNode(parentPath)
      parent.children.push(node)
    }
    
    return node
  }

  // Build tree from categories
  sortedCategories.forEach(category => {
    const parts = category.name.split('/')
    const node = getOrCreateNode(parts)
    node.count = category.count
    
    // Update all ancestor counts
    for (let i = parts.length - 1; i >= 1; i--) {
      const ancestorPath = parts.slice(0, i).join('/')
      const ancestor = nodeMap.get(ancestorPath)
      if (ancestor) {
        ancestor.count += category.count
      }
    }
  })

  return root.sort((a, b) => a.name.localeCompare(b.name))
})

function toggleCategory(categoryFullName: string) {
  if (expandedCategories.value.has(categoryFullName)) {
    expandedCategories.value.delete(categoryFullName)
  } else {
    expandedCategories.value.add(categoryFullName)
  }
}
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
</style>
