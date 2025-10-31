<template>
  <div class="dashboard">
    <header class="header">
      <div class="mb-6">
        <h1 class="text-3xl font-semibold text-gray-900 mb-2">PrismQ Module Control Panel</h1>
        <div class="stats">
          <span class="stat-item">{{ modules.length }} Modules</span>
          <span class="stat-item" v-if="activeRuns > 0">{{ activeRuns }} Running</span>
          <router-link to="/runs" class="stat-link">View Run History</router-link>
        </div>
      </div>
    </header>

    <!-- Active Runs Section -->
    <div v-if="!loading && !error" class="mb-6">
      <ActiveRuns @runs-updated="updateActiveRunsCount" />
    </div>

    <!-- Search and Filters -->
    <div class="filters" v-if="!loading && !error">
      <input 
        v-model="searchQuery" 
        placeholder="Search modules..." 
        class="search-input"
      />
      <select v-model="categoryFilter" class="category-select">
        <option value="">All Categories</option>
        <option v-for="cat in categories" :key="cat">{{ cat }}</option>
      </select>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      <p class="mt-4 text-gray-600">Loading modules...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
      <p class="font-bold">Error loading modules</p>
      <p class="text-sm">{{ error }}</p>
    </div>

    <!-- Modules grid -->
    <div v-else class="module-grid">
      <ModuleCard
        v-for="module in filteredModules"
        :key="module.id"
        :module="module"
        @launch="openLaunchModal"
      />
    </div>

    <!-- Empty state -->
    <div v-if="!loading && !error && filteredModules.length === 0" class="text-center py-12">
      <p class="text-gray-600">
        {{ searchQuery || categoryFilter ? 'No modules match your filters' : 'No modules available' }}
      </p>
    </div>

    <!-- Launch Modal -->
    <ModuleLaunchModal 
      v-if="showLaunchModal && selectedModule"
      :module="selectedModule"
      @close="closeLaunchModal"
      @launch="handleLaunch"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import ModuleCard from '@/components/ModuleCard.vue'
import ModuleLaunchModal from '@/components/ModuleLaunchModal.vue'
import ActiveRuns from '@/components/ActiveRuns.vue'
import { moduleService } from '@/services/modules'
import type { Module } from '@/types/module'

const modules = ref<Module[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const searchQuery = ref('')
const categoryFilter = ref('')
const showLaunchModal = ref(false)
const selectedModule = ref<Module | null>(null)
const activeRuns = ref(0)

// Compute unique categories
const categories = computed(() => {
  const uniqueCategories = new Set(modules.value.map(m => m.category))
  return Array.from(uniqueCategories).sort()
})

// Filter modules based on search and category
const filteredModules = computed(() => {
  let filtered = modules.value

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(m => 
      m.name.toLowerCase().includes(query) ||
      m.description.toLowerCase().includes(query) ||
      m.tags?.some(tag => tag.toLowerCase().includes(query))
    )
  }

  // Filter by category
  if (categoryFilter.value) {
    filtered = filtered.filter(m => m.category === categoryFilter.value)
  }

  return filtered
})

async function loadModules() {
  try {
    loading.value = true
    error.value = null
    modules.value = await moduleService.listModules()
  } catch (err: any) {
    error.value = err.message || 'Failed to load modules'
    console.error('Error loading modules:', err)
  } finally {
    loading.value = false
  }
}

function openLaunchModal(module: Module) {
  selectedModule.value = module
  showLaunchModal.value = true
}

function closeLaunchModal() {
  showLaunchModal.value = false
  selectedModule.value = null
}

async function handleLaunch(parameters: Record<string, any>, saveConfig: boolean) {
  if (!selectedModule.value) return

  try {
    const run = await moduleService.launchModule(
      selectedModule.value.id,
      parameters,
      saveConfig
    )
    console.log('Run started:', run)
    alert(`Module "${selectedModule.value.name}" launched successfully! Run ID: ${run.id}`)
    closeLaunchModal()
  } catch (err: any) {
    console.error('Error starting run:', err)
    alert(`Failed to start module: ${err.message}`)
  }
}

function updateActiveRunsCount(count: number) {
  activeRuns.value = count
}

onMounted(() => {
  loadModules()
})
</script>

<style scoped>
.dashboard {
  /* Dashboard-specific styles */
}

.header {
  @apply mb-6;
}

.stats {
  @apply flex gap-4 text-sm text-gray-600 mt-2;
}

.stat-item {
  @apply px-3 py-1 bg-gray-100 rounded-full;
}

.stat-link {
  @apply px-3 py-1 bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-full transition-colors;
}

.filters {
  @apply flex gap-4 mb-6;
}

.search-input {
  @apply flex-1 px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500;
}

.category-select {
  @apply px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white;
}

.module-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6;
}
</style>
