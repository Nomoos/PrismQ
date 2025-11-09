<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 py-4">
        <h1 class="text-xl font-bold text-gray-900">Settings</h1>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-6 space-y-4">
      <!-- Worker Configuration -->
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Worker Configuration</h2>
        <p class="text-sm text-gray-600 mb-4">
          Set your worker ID for claiming and completing tasks
        </p>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Worker ID
            </label>
            <input
              v-model="workerIdInput"
              type="text"
              placeholder="e.g., frontend-worker-1"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p class="text-xs text-gray-500 mt-1">
              This ID will be used when claiming and completing tasks
            </p>
          </div>
          
          <button
            @click="saveWorkerId"
            class="btn-primary min-h-[44px] w-full"
          >
            Save Worker ID
          </button>
          
          <div v-if="saveMessage" class="p-3 rounded-lg" :class="saveSuccess ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'">
            {{ saveMessage }}
          </div>
        </div>
      </div>

      <!-- API Configuration -->
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">API Configuration</h2>
        <p class="text-sm text-gray-600 mb-4">
          Configure connection to Backend/TaskManager API
        </p>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              API Base URL
            </label>
            <input
              type="text"
              :value="apiBaseUrl"
              readonly
              class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              API Key
            </label>
            <input
              type="password"
              :value="apiKey"
              readonly
              class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
            />
          </div>
          
          <p class="text-xs text-gray-500">
            Settings are configured via environment variables (.env file)
          </p>
        </div>
      </div>

      <!-- App Information -->
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Application Info</h2>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-600">Version:</span>
            <span class="font-medium">0.1.0</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Environment:</span>
            <span class="font-medium">{{ environment }}</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api'
const apiKey = import.meta.env.VITE_API_KEY ? '••••••••' : 'Not configured'
const environment = import.meta.env.MODE

const workerIdInput = ref('')
const saveMessage = ref('')
const saveSuccess = ref(false)

// Load worker ID from localStorage on mount
onMounted(() => {
  const savedWorkerId = localStorage.getItem('workerId')
  if (savedWorkerId) {
    workerIdInput.value = savedWorkerId
  } else {
    // Default worker ID
    workerIdInput.value = 'frontend-worker-1'
  }
})

function saveWorkerId() {
  if (!workerIdInput.value.trim()) {
    saveMessage.value = 'Worker ID cannot be empty'
    saveSuccess.value = false
    return
  }

  try {
    localStorage.setItem('workerId', workerIdInput.value.trim())
    saveMessage.value = 'Worker ID saved successfully!'
    saveSuccess.value = true
    
    // Clear message after 3 seconds
    setTimeout(() => {
      saveMessage.value = ''
    }, 3000)
  } catch (e) {
    saveMessage.value = 'Failed to save Worker ID'
    saveSuccess.value = false
  }
}
</script>
