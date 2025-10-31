# Issue #105: Develop Frontend UI for Module Selection & Launch

**Type**: Feature  
**Priority**: High  
**Status**: Done  
**Completed**: 2025-10-31  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 2-3 weeks  
**Dependencies**: #101 (Project Structure), #102 (API Design)  
**Can be parallelized with**: #103 (Backend Module Runner)

---

## Description

Create the Vue 3 frontend interface for discovering, selecting, and launching PrismQ modules. This includes a dashboard to display available modules, forms for parameter input, and UI to initiate module execution.

## Components

### 1. Dashboard View (`src/views/Dashboard.vue`)

Main page displaying all available modules in a grid/list layout.

```vue
<template>
  <div class="dashboard">
    <header class="header">
      <h1>PrismQ Module Control Panel</h1>
      <div class="stats">
        <span>{{ modules.length }} Modules</span>
        <span>{{ activeRuns.length }} Running</span>
      </div>
    </header>
    
    <div class="filters">
      <input v-model="searchQuery" placeholder="Search modules..." />
      <select v-model="categoryFilter">
        <option value="">All Categories</option>
        <option v-for="cat in categories" :key="cat">{{ cat }}</option>
      </select>
    </div>
    
    <div class="module-grid">
      <ModuleCard 
        v-for="module in filteredModules" 
        :key="module.id"
        :module="module"
        @launch="openLaunchModal"
      />
    </div>
    
    <ModuleLaunchModal 
      v-if="showLaunchModal"
      :module="selectedModule"
      @close="showLaunchModal = false"
      @launch="handleLaunch"
    />
  </div>
</template>
```

### 2. ModuleCard Component (`src/components/ModuleCard.vue`)

Display individual module information with quick launch button.

```vue
<template>
  <div class="module-card">
    <div class="module-header">
      <h3>{{ module.name }}</h3>
      <span class="category-badge">{{ module.category }}</span>
    </div>
    
    <p class="description">{{ module.description }}</p>
    
    <div class="module-stats">
      <span>{{ module.total_runs }} runs</span>
      <span>{{ module.success_rate }}% success</span>
    </div>
    
    <div class="module-tags">
      <span v-for="tag in module.tags" :key="tag" class="tag">
        {{ tag }}
      </span>
    </div>
    
    <button 
      @click="$emit('launch', module)"
      class="btn-primary"
      :disabled="isRunning"
    >
      {{ isRunning ? 'Running...' : 'Launch Module' }}
    </button>
  </div>
</template>
```

### 3. ModuleLaunchModal Component (`src/components/ModuleLaunchModal.vue`)

Modal dialog for entering module parameters before launch.

```vue
<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <header class="modal-header">
        <h2>Launch: {{ module.name }}</h2>
        <button @click="$emit('close')" class="btn-close">×</button>
      </header>
      
      <form @submit.prevent="handleSubmit" class="parameter-form">
        <div 
          v-for="param in module.parameters" 
          :key="param.name"
          class="form-field"
        >
          <label :for="param.name">
            {{ param.description || param.name }}
            <span v-if="param.required" class="required">*</span>
          </label>
          
          <!-- Text input -->
          <input 
            v-if="param.type === 'text' || param.type === 'password'"
            :id="param.name"
            v-model="formData[param.name]"
            :type="param.type"
            :required="param.required"
            :placeholder="param.default"
          />
          
          <!-- Number input -->
          <input 
            v-else-if="param.type === 'number'"
            :id="param.name"
            v-model.number="formData[param.name]"
            type="number"
            :min="param.min"
            :max="param.max"
            :required="param.required"
          />
          
          <!-- Select dropdown -->
          <select 
            v-else-if="param.type === 'select'"
            :id="param.name"
            v-model="formData[param.name]"
            :required="param.required"
          >
            <option 
              v-for="option in param.options" 
              :key="option"
              :value="option"
            >
              {{ option }}
            </option>
          </select>
          
          <!-- Checkbox -->
          <input 
            v-else-if="param.type === 'checkbox'"
            :id="param.name"
            v-model="formData[param.name]"
            type="checkbox"
          />
        </div>
        
        <div class="form-actions">
          <label>
            <input type="checkbox" v-model="saveConfig" />
            Save configuration
          </label>
          
          <div class="buttons">
            <button type="button" @click="$emit('close')" class="btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? 'Launching...' : 'Launch' }}
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Module } from '@/types/module'
import { moduleService } from '@/services/modules'

const props = defineProps<{
  module: Module
}>()

const emit = defineEmits<{
  close: []
  launch: [parameters: Record<string, any>]
}>()

const formData = ref<Record<string, any>>({})
const saveConfig = ref(true)
const isSubmitting = ref(false)

onMounted(async () => {
  // Load saved configuration
  const config = await moduleService.getConfig(props.module.id)
  formData.value = config.parameters || {}
  
  // Set defaults for missing values
  props.module.parameters.forEach(param => {
    if (!(param.name in formData.value)) {
      formData.value[param.name] = param.default
    }
  })
})

async function handleSubmit() {
  isSubmitting.value = true
  try {
    emit('launch', {
      parameters: formData.value,
      saveConfig: saveConfig.value
    })
  } finally {
    isSubmitting.value = false
  }
}
</script>
```

### 4. API Service (`src/services/modules.ts`)

TypeScript service for API calls.

```typescript
import axios from 'axios'
import type { Module, ModuleConfig, Run } from '@/types/module'

const API_BASE = 'http://localhost:8000/api'

class ModuleService {
  async getModules(): Promise<Module[]> {
    const response = await axios.get(`${API_BASE}/modules`)
    return response.data.modules
  }
  
  async getModule(moduleId: string): Promise<Module> {
    const response = await axios.get(`${API_BASE}/modules/${moduleId}`)
    return response.data
  }
  
  async getConfig(moduleId: string): Promise<ModuleConfig> {
    const response = await axios.get(`${API_BASE}/modules/${moduleId}/config`)
    return response.data
  }
  
  async saveConfig(moduleId: string, parameters: Record<string, any>): Promise<void> {
    await axios.post(`${API_BASE}/modules/${moduleId}/config`, { parameters })
  }
  
  async launchModule(moduleId: string, parameters: Record<string, any>, saveConfig: boolean): Promise<Run> {
    const response = await axios.post(`${API_BASE}/modules/${moduleId}/run`, {
      parameters,
      save_config: saveConfig
    })
    return response.data
  }
}

export const moduleService = new ModuleService()
```

### 5. TypeScript Types (`src/types/module.ts`)

```typescript
export interface ModuleParameter {
  name: string
  type: 'text' | 'number' | 'select' | 'checkbox' | 'password'
  default?: string | number | boolean
  options?: string[]
  required: boolean
  description: string
  min?: number
  max?: number
}

export interface Module {
  id: string
  name: string
  description: string
  category: string
  version: string
  script_path: string
  parameters: ModuleParameter[]
  tags: string[]
  status: 'active' | 'inactive' | 'maintenance'
  last_run?: string
  total_runs: number
  success_rate: number
}

export interface ModuleConfig {
  module_id: string
  parameters: Record<string, any>
  updated_at: string
}

export interface Run {
  run_id: string
  module_id: string
  module_name: string
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'
  created_at: string
  parameters: Record<string, any>
}
```

### 6. Tailwind Styling

```css
/* Custom styles in src/assets/main.css */

.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
}

.module-card {
  @apply border rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow bg-white;
}

.module-header {
  @apply flex justify-between items-start mb-3;
}

.category-badge {
  @apply px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm;
}

.modal-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}

.modal-content {
  @apply bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto;
}

.parameter-form {
  @apply p-6 space-y-4;
}

.form-field {
  @apply space-y-2;
}

.btn-primary {
  @apply px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors;
}

.btn-secondary {
  @apply px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors;
}
```

---

## Tasks

### Component Development
- [x] Create Dashboard view with module grid
- [x] Implement ModuleCard component
- [x] Implement ModuleLaunchModal with dynamic form
- [x] Add search and filter functionality
- [x] Implement responsive layout (desktop-first for this use case)

### Services & State
- [x] Create API service layer (modules.ts)
- [x] Set up Pinia store for global state (optional)
- [x] Implement error handling for API calls
- [x] Add loading states

### TypeScript Types
- [x] Define Module interface
- [x] Define ModuleParameter interface
- [x] Define Run interface
- [x] Define API response types

### Styling
- [x] Configure Tailwind CSS
- [x] Create component styles
- [x] Add hover effects and transitions
- [x] Ensure accessibility (ARIA labels, keyboard navigation)

### Testing
- [x] Component unit tests (Vitest)
- [x] E2E tests for user workflows (Playwright)
- [x] Test form validation
- [x] Test API error scenarios

### Bug Fixes
- [x] Add missing `enabled` field to backend Module model

---

## Acceptance Criteria

- [x] Dashboard displays all available modules
- [x] Module cards show name, description, category, stats
- [x] Click on "Launch" opens parameter form modal
- [x] Form dynamically renders based on module parameters
- [x] Form loads saved configuration on open
- [x] Form validates required fields
- [x] Launch button triggers API call and shows loading state
- [x] Search and category filter work correctly
- [x] UI is responsive and accessible
- [x] Error messages display on API failures

## Related Issues

- **Depends on**: #101 (Project Structure), #102 (API Design)
- **Parallel**: #103 (Backend Module Runner)
- **Next**: #107 (Live Logs Display)

## References

- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Axios Documentation](https://axios-http.com/docs/intro)
