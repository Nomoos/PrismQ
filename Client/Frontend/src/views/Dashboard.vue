<template>
  <div class="dashboard-container">
    <!-- Left Sidebar -->
    <LeftSidebar
      v-if="!loading && !error"
      :current-filter="currentFilter"
      :selected-category="selectedCategory"
      :total-modules="modules.length"
      :most-used-count="mostUsedModules.length"
      :recent-count="recentModules.length"
      :categories="categoryStats"
      @filter-change="handleFilterChange"
    />

    <!-- Main Content -->
    <div class="dashboard-main">
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

      <!-- Tabs -->
      <ModuleTabs
        v-if="!loading && !error"
        :tabs="tabs"
        :current-tab="currentTab"
        @tab-change="handleTabChange"
      />

      <!-- Search and Filters -->
      <div class="filters" v-if="!loading && !error">
        <input 
          v-model="searchQuery" 
          placeholder="Search modules..." 
          class="search-input"
        />
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
          {{ searchQuery || currentFilter !== 'all' ? 'No modules match your filters' : 'No modules available' }}
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import ModuleCard from '@/components/ModuleCard.vue'
import ModuleLaunchModal from '@/components/ModuleLaunchModal.vue'
import ModuleTabs from '@/components/ModuleTabs.vue'
import LeftSidebar from '@/components/LeftSidebar.vue'
import ActiveRuns from '@/components/ActiveRuns.vue'
import { moduleService } from '@/services/modules'
import type { Module } from '@/types/module'

const modules = ref<Module[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const searchQuery = ref('')
const currentFilter = ref('all')
const selectedCategory = ref<string>()
const currentTab = ref('all')
const showLaunchModal = ref(false)
const selectedModule = ref<Module | null>(null)
const activeRuns = ref(0)

// Compute tabs with counts
const tabs = computed(() => {
  const allCount = modules.value.length
  const categoryCount = selectedCategory.value 
    ? modules.value.filter(m => m.category === selectedCategory.value).length 
    : 0
  
  return [
    { id: 'all', label: 'All Modules', icon: '📋', count: allCount },
    { id: 'category', label: 'By Category', icon: '📁', count: categoryCount },
    { id: 'usage', label: 'By Usage', icon: '🔥' },
    { id: 'recent', label: 'Recent', icon: '🕐' },
  ]
})

// Compute category statistics
const categoryStats = computed(() => {
  const categoryMap = new Map<string, number>()
  
  modules.value.forEach(m => {
    const count = categoryMap.get(m.category) || 0
    categoryMap.set(m.category, count + 1)
  })
  
  return Array.from(categoryMap.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => a.name.localeCompare(b.name))
})

// Most used modules (modules with highest total_runs)
const mostUsedModules = computed(() => {
  return modules.value
    .filter(m => m.total_runs > 0)
    .sort((a, b) => b.total_runs - a.total_runs)
    .slice(0, 10)
})

// Recently used modules (modules with last_run)
const recentModules = computed(() => {
  return modules.value
    .filter(m => m.last_run)
    .sort((a, b) => {
      const dateA = new Date(a.last_run!).getTime()
      const dateB = new Date(b.last_run!).getTime()
      return dateB - dateA
    })
    .slice(0, 10)
})

// Filter modules based on current view and search
const filteredModules = computed(() => {
  let filtered = modules.value

  // Apply tab/filter
  if (currentTab.value === 'usage' || currentFilter.value === 'most-used') {
    filtered = mostUsedModules.value
  } else if (currentTab.value === 'recent' || currentFilter.value === 'recent') {
    filtered = recentModules.value
  } else if ((currentFilter.value === 'category' || currentTab.value === 'category') && selectedCategory.value) {
    filtered = filtered.filter(m => m.category === selectedCategory.value)
  }

  // Apply search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(m => 
      m.name.toLowerCase().includes(query) ||
      m.description.toLowerCase().includes(query) ||
      m.tags?.some(tag => tag.toLowerCase().includes(query))
    )
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

function handleTabChange(tabId: string) {
  currentTab.value = tabId
  
  // Reset filter when switching tabs
  if (tabId === 'all') {
    currentFilter.value = 'all'
    selectedCategory.value = undefined
  } else if (tabId === 'usage') {
    currentFilter.value = 'most-used'
  } else if (tabId === 'recent') {
    currentFilter.value = 'recent'
  }
}

function handleFilterChange(filter: string, category?: string) {
  currentFilter.value = filter
  selectedCategory.value = category
  
  // Update tab based on filter
  if (filter === 'all') {
    currentTab.value = 'all'
  } else if (filter === 'most-used') {
    currentTab.value = 'usage'
  } else if (filter === 'recent') {
    currentTab.value = 'recent'
  } else if (filter === 'category') {
    currentTab.value = 'category'
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
    alert(`Module "${selectedModule.value.name}" launched successfully! Run ID: ${run.run_id}`)
    closeLaunchModal()
    
    // Reload modules to update statistics
    await loadModules()
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
.dashboard-container {
  @apply flex min-h-screen bg-gray-50;
}

.dashboard-main {
  @apply flex-1 overflow-auto;
}

.header {
  @apply mb-6 px-6 pt-6;
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
  @apply px-6 mb-6;
}

.search-input {
  @apply w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500;
}

.module-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 px-6 pb-6;
}
</style>
