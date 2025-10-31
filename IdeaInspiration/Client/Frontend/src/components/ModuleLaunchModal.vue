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
            v-if="param.type === 'text'"
            :id="param.name"
            v-model="formData[param.name]"
            type="text"
            :required="param.required"
            :placeholder="String(param.default || '')"
            :class="{ 'input-error': errors[param.name] }"
          />
          
          <!-- Password input -->
          <input 
            v-else-if="param.type === 'password'"
            :id="param.name"
            v-model="formData[param.name]"
            type="password"
            :required="param.required"
            :placeholder="String(param.default || '')"
            :class="{ 'input-error': errors[param.name] }"
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
            :class="{ 'input-error': errors[param.name] }"
          />
          
          <!-- Select dropdown -->
          <select 
            v-else-if="param.type === 'select'"
            :id="param.name"
            v-model="formData[param.name]"
            :required="param.required"
            :class="{ 'input-error': errors[param.name] }"
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
          <div v-else-if="param.type === 'checkbox'" class="checkbox-wrapper">
            <input 
              :id="param.name"
              v-model="formData[param.name]"
              type="checkbox"
            />
          </div>
          
          <!-- Error message -->
          <div v-if="errors[param.name]" class="error-message">
            {{ errors[param.name] }}
          </div>
        </div>
        
        <div class="form-actions">
          <div class="left-actions">
            <label class="save-config-label">
              <input type="checkbox" v-model="saveConfig" />
              Save configuration
            </label>
            
            <button 
              type="button" 
              @click="resetToDefaults" 
              class="btn-text"
              :disabled="isSubmitting"
            >
              Reset to defaults
            </button>
          </div>
          
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
import { useNotificationStore } from '@/stores/notifications'

const props = defineProps<{
  module: Module
}>()

const emit = defineEmits<{
  close: []
  launch: [parameters: Record<string, any>, saveConfig: boolean]
}>()

const formData = ref<Record<string, any>>({})
const saveConfig = ref(true)
const isSubmitting = ref(false)
const errors = ref<Record<string, string>>({})
const notifications = useNotificationStore()

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

/**
 * Validate form data against parameter definitions.
 * 
 * @returns true if valid, false otherwise
 */
function validateForm(): boolean {
  errors.value = {}
  
  for (const param of props.module.parameters) {
    const value = formData.value[param.name]
    
    // Required check
    if (param.required && (value === undefined || value === '' || value === null)) {
      errors.value[param.name] = `${param.description || param.name} is required`
      continue
    }
    
    // Skip further validation if value is empty and not required
    if (value === undefined || value === '' || value === null) {
      continue
    }
    
    // Type-specific validation
    if (param.type === 'number') {
      const num = Number(value)
      if (isNaN(num)) {
        errors.value[param.name] = 'Must be a number'
      } else if (param.min !== undefined && num < param.min) {
        errors.value[param.name] = `Must be at least ${param.min}`
      } else if (param.max !== undefined && num > param.max) {
        errors.value[param.name] = `Must be at most ${param.max}`
      }
    } else if (param.type === 'select' && param.options) {
      if (!param.options.includes(value)) {
        errors.value[param.name] = `Must be one of: ${param.options.join(', ')}`
      }
    }
  }
  
  return Object.keys(errors.value).length === 0
}

async function handleSubmit() {
  // Validate form
  if (!validateForm()) {
    notifications.error({
      title: 'Validation Error',
      message: 'Please fix the errors in the form before submitting.',
    })
    return
  }
  
  isSubmitting.value = true
  try {
    emit('launch', formData.value, saveConfig.value)
  } finally {
    isSubmitting.value = false
  }
}

async function resetToDefaults() {
  try {
    // Delete saved configuration
    await moduleService.deleteConfig(props.module.id)
    
    // Reset form to defaults
    formData.value = {}
    props.module.parameters.forEach(param => {
      formData.value[param.name] = param.default
    })
    
    // Clear errors
    errors.value = {}
    
    notifications.success({
      title: 'Configuration Reset',
      message: 'Configuration has been reset to defaults.',
    })
  } catch (error) {
    console.error('Failed to reset configuration:', error)
  }
}
</script>

<style scoped>
.modal-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}

.modal-content {
  @apply bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto;
}

.modal-header {
  @apply flex justify-between items-center p-6 border-b border-gray-200;
}

.modal-header h2 {
  @apply text-2xl font-semibold text-gray-900;
}

.btn-close {
  @apply text-gray-400 hover:text-gray-600 text-3xl font-light leading-none;
}

.parameter-form {
  @apply p-6 space-y-4;
}

.form-field {
  @apply space-y-2;
}

.form-field label {
  @apply block text-sm font-medium text-gray-700;
}

.form-field .required {
  @apply text-red-500 ml-1;
}

.form-field input[type="text"],
.form-field input[type="password"],
.form-field input[type="number"],
.form-field select {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500;
}

.input-error {
  @apply border-red-500 focus:ring-red-500 focus:border-red-500;
}

.error-message {
  @apply text-sm text-red-600 mt-1;
}

.checkbox-wrapper {
  @apply flex items-center;
}

.checkbox-wrapper input[type="checkbox"] {
  @apply h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded;
}

.form-actions {
  @apply mt-6 pt-4 border-t border-gray-200 flex justify-between items-center;
}

.left-actions {
  @apply flex items-center gap-4;
}

.save-config-label {
  @apply flex items-center gap-2 text-sm text-gray-700 cursor-pointer;
}

.save-config-label input[type="checkbox"] {
  @apply h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded;
}

.btn-text {
  @apply text-sm text-blue-600 hover:text-blue-700 underline disabled:text-gray-400 disabled:cursor-not-allowed;
}

.buttons {
  @apply flex gap-3;
}

.btn-primary {
  @apply px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors;
}

.btn-secondary {
  @apply px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors;
}
</style>
