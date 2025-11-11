<template>
  <div class="min-h-screen bg-gray-50 dark:bg-dark-canvas-default pb-20">
    <!-- Header -->
    <header 
      role="banner"
      class="bg-white dark:bg-dark-surface-default shadow-sm sticky top-0 z-10 dark:border-b dark:border-dark-border-default"
    >
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center">
        <button
          @click="router.back()"
          class="mr-3 p-2 hover:bg-gray-100 dark:hover:bg-dark-surface-overlay rounded-lg"
          aria-label="Go back"
        >
          ← Back
        </button>
        <h1 class="text-xl font-bold text-gray-900 dark:text-dark-text-primary">Create Task</h1>
      </div>
    </header>

    <main 
      id="main-content"
      role="main"
      aria-label="Create task form"
      class="max-w-7xl mx-auto px-4 py-6 space-y-4"
      tabindex="-1"
    >
      <!-- Loading State -->
      <LoadingState v-if="loading" message="Loading task types..." />

      <!-- Error State -->
      <ErrorDisplay 
        v-else-if="error" 
        :message="error"
        :retryable="false"
      />

      <!-- Task Creation Form -->
      <form v-else @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Task Type Selection -->
        <section class="card">
          <h2 class="text-lg font-semibold mb-4 dark:text-dark-text-primary">Select Task Type</h2>
          
          <label for="task-type" class="block text-sm font-medium text-gray-700 dark:text-dark-text-secondary mb-2">
            Task Type *
          </label>
          <select
            id="task-type"
            v-model="selectedTypeId"
            @change="onTaskTypeChange"
            required
            class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border-default rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-dark-surface-default dark:text-dark-text-primary"
          >
            <option value="">-- Select a task type --</option>
            <optgroup v-if="mostUsedTypes.length > 0" label="Most Used">
              <option 
                v-for="type in mostUsedTypes" 
                :key="type.id" 
                :value="type.id"
              >
                {{ type.name }} (used {{ type.usage_count }} times)
              </option>
            </optgroup>
            <optgroup label="All Task Types">
              <option 
                v-for="type in otherTypes" 
                :key="type.id" 
                :value="type.id"
              >
                {{ type.name }}
              </option>
            </optgroup>
          </select>
        </section>

        <!-- Task Parameters -->
        <section v-if="selectedType" class="card">
          <h2 class="text-lg font-semibold mb-4 dark:text-dark-text-primary">Task Parameters</h2>
          
          <div v-if="!selectedType.param_schema || !selectedType.param_schema.properties" class="text-gray-600 dark:text-dark-text-secondary">
            This task type has no parameters.
          </div>
          
          <div v-else class="space-y-4">
            <div 
              v-for="(schema, paramName) in selectedType.param_schema.properties" 
              :key="String(paramName)"
              class="form-group"
            >
              <label 
                :for="`param-${paramName}`" 
                class="block text-sm font-medium text-gray-700 dark:text-dark-text-secondary mb-2"
              >
                {{ paramName }}
                <span v-if="isRequired(String(paramName))" class="text-red-500">*</span>
              </label>
              
              <!-- String input -->
              <input
                v-if="schema.type === 'string' && !schema.enum"
                :id="`param-${paramName}`"
                v-model="taskParams[String(paramName)]"
                type="text"
                :required="isRequired(String(paramName))"
                :minlength="schema.minLength"
                :maxlength="schema.maxLength"
                :placeholder="schema.description || `Enter ${paramName}`"
                class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border-default rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-dark-surface-default dark:text-dark-text-primary"
              />
              
              <!-- Enum select -->
              <select
                v-else-if="schema.type === 'string' && schema.enum"
                :id="`param-${paramName}`"
                v-model="taskParams[String(paramName)]"
                :required="isRequired(String(paramName))"
                class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border-default rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-dark-surface-default dark:text-dark-text-primary"
              >
                <option value="">-- Select --</option>
                <option v-for="option in schema.enum" :key="option" :value="option">
                  {{ option }}
                </option>
              </select>
              
              <!-- Number input -->
              <input
                v-else-if="schema.type === 'integer' || schema.type === 'number'"
                :id="`param-${paramName}`"
                v-model.number="taskParams[String(paramName)]"
                :type="schema.type === 'integer' ? 'number' : 'text'"
                :required="isRequired(String(paramName))"
                :min="schema.minimum"
                :max="schema.maximum"
                :step="schema.type === 'integer' ? 1 : 'any'"
                :placeholder="schema.description || `Enter ${paramName}`"
                class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border-default rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-dark-surface-default dark:text-dark-text-primary"
              />
              
              <!-- Boolean checkbox -->
              <div v-else-if="schema.type === 'boolean'" class="flex items-center">
                <input
                  :id="`param-${paramName}`"
                  v-model="taskParams[String(paramName)]"
                  type="checkbox"
                  class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <span class="ml-2 text-sm text-gray-600 dark:text-dark-text-secondary">
                  {{ schema.description || paramName }}
                </span>
              </div>
              
              <!-- Textarea for objects/arrays or long strings -->
              <textarea
                v-else
                :id="`param-${paramName}`"
                v-model="taskParams[String(paramName)]"
                :required="isRequired(String(paramName))"
                :placeholder="schema.description || `Enter ${paramName} (JSON format)`"
                rows="4"
                class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border-default rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-dark-surface-default dark:text-dark-text-primary font-mono text-sm"
              ></textarea>
              
              <!-- Help text -->
              <p v-if="schema.description" class="mt-1 text-xs text-gray-500 dark:text-dark-text-tertiary">
                {{ schema.description }}
              </p>
            </div>
          </div>
        </section>

        <!-- Priority (Optional) -->
        <section class="card">
          <h2 class="text-lg font-semibold mb-4 dark:text-dark-text-primary">Priority (Optional)</h2>
          
          <label for="priority" class="block text-sm font-medium text-gray-700 dark:text-dark-text-secondary mb-2">
            Task Priority (higher = more important)
          </label>
          <input
            id="priority"
            v-model.number="priority"
            type="number"
            min="0"
            max="100"
            placeholder="0"
            class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border-default rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-dark-surface-default dark:text-dark-text-primary"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-dark-text-tertiary">
            Default is 0. Higher values give the task higher priority in the queue.
          </p>
        </section>

        <!-- Submit -->
        <div class="flex gap-3">
          <button
            type="submit"
            :disabled="!selectedType || creating"
            class="btn-primary flex-1 min-h-[44px]"
            :class="{ 'opacity-50 cursor-not-allowed': !selectedType || creating }"
          >
            <span v-if="creating">Creating...</span>
            <span v-else>Create Task</span>
          </button>
          
          <button
            type="button"
            @click="router.back()"
            class="btn-secondary flex-1 min-h-[44px]"
          >
            Cancel
          </button>
        </div>
      </form>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { taskService } from '../services/taskService'
import LoadingState from '../components/base/LoadingState.vue'
import ErrorDisplay from '../components/base/ErrorDisplay.vue'
import type { TaskType } from '../types'

const router = useRouter()

const loading = ref(true)
const error = ref<string | null>(null)
const creating = ref(false)
const taskTypes = ref<TaskType[]>([])
const selectedTypeId = ref<number | ''>('')
const taskParams = ref<Record<string, any>>({})
const priority = ref(0)

const selectedType = computed(() => {
  if (!selectedTypeId.value) return null
  return taskTypes.value.find(t => t.id === selectedTypeId.value) || null
})

// Split types into most used and others
const mostUsedTypes = computed(() => {
  return taskTypes.value
    .filter(t => t.usage_count && t.usage_count > 0)
    .sort((a, b) => (b.usage_count || 0) - (a.usage_count || 0))
    .slice(0, 5) // Top 5 most used
})

const otherTypes = computed(() => {
  const mostUsedIds = new Set(mostUsedTypes.value.map(t => t.id))
  return taskTypes.value.filter(t => !mostUsedIds.has(t.id))
})

function isRequired(paramName: string): boolean {
  if (!selectedType.value?.param_schema?.required) return false
  return selectedType.value.param_schema.required.includes(paramName)
}

function onTaskTypeChange() {
  // Reset parameters when task type changes
  taskParams.value = {}
}

async function loadTaskTypes() {
  try {
    loading.value = true
    error.value = null
    
    const response = await taskService.getTaskTypes(true)
    if (response.success && response.data) {
      taskTypes.value = response.data
    } else {
      error.value = 'Failed to load task types'
    }
  } catch (err) {
    console.error('Failed to load task types:', err)
    error.value = err instanceof Error ? err.message : 'Failed to load task types'
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!selectedType.value) return
  
  creating.value = true
  error.value = null
  
  try {
    // Create the task
    const response = await taskService.createTask({
      type: selectedType.value.name,
      params: taskParams.value,
      priority: priority.value || 0
    })
    
    if (response.success && response.data) {
      // Navigate to the created task
      await router.push(`/tasks/${response.data.id}`)
    } else {
      error.value = response.message || 'Failed to create task'
    }
  } catch (err) {
    console.error('Failed to create task:', err)
    error.value = err instanceof Error ? err.message : 'Failed to create task'
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  loadTaskTypes()
})
</script>
