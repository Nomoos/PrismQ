<template>
  <nav 
    aria-label="Breadcrumb navigation"
    class="bg-white dark:bg-dark-surface-default border-b border-gray-200 dark:border-dark-border-default"
  >
    <div class="max-w-7xl mx-auto px-4 py-3">
      <ol class="flex items-center space-x-2 text-sm" role="list">
        <li
          v-for="(crumb, index) in navigation.breadcrumbs.value"
          :key="crumb.level"
          class="flex items-center"
        >
          <span v-if="index > 0" class="mx-2 text-gray-400 dark:text-dark-text-tertiary">→</span>
          
          <button
            v-if="!crumb.isActive"
            @click="navigation.navigateTo(crumb.level)"
            class="text-primary-600 dark:text-dark-primary-text hover:text-primary-800 dark:hover:text-primary-400 hover:underline"
            :aria-label="`Navigate to ${crumb.label}`"
          >
            {{ crumb.label }}
          </button>
          
          <span
            v-else
            class="text-gray-900 dark:text-dark-text-primary font-semibold"
            aria-current="page"
          >
            {{ crumb.label }}
          </span>
        </li>
      </ol>
      
      <!-- Child Navigation Menu -->
      <div 
        v-if="navigation.availableChildren.value.length > 0" 
        class="mt-4"
      >
        <p class="text-xs font-semibold text-gray-700 dark:text-dark-text-secondary mb-2">
          Navigate to:
        </p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="child in navigation.availableChildren.value"
            :key="child"
            @click="navigation.navigateTo(child)"
            class="btn-secondary text-xs px-3 py-1.5 hover:bg-primary-50 dark:hover:bg-dark-primary-subtle"
            :aria-label="`Navigate to ${getChildLabel(child)}`"
          >
            {{ getChildLabel(child) }}
          </button>
        </div>
      </div>
      
      <!-- Parent Navigation -->
      <div v-if="navigation.parentNode.value" class="mt-3">
        <button
          @click="navigation.goToParent()"
          class="btn-secondary text-xs px-3 py-1"
          aria-label="Go to parent"
        >
          ↑ Back to {{ navigation.parentNode.value }}
        </button>
      </div>
      
      <!-- Navigation Controls -->
      <div class="mt-3 flex gap-2">
        <button
          @click="navigation.goBack()"
          :disabled="!navigation.canGoBack.value"
          class="btn-secondary text-xs px-3 py-1"
          :class="{ 'opacity-50 cursor-not-allowed': !navigation.canGoBack.value }"
          aria-label="Go back in history"
        >
          ← Back
        </button>
        
        <button
          @click="navigation.goForward()"
          :disabled="!navigation.canGoForward.value"
          class="btn-secondary text-xs px-3 py-1"
          :class="{ 'opacity-50 cursor-not-allowed': !navigation.canGoForward.value }"
          aria-label="Go forward in history"
        >
          Forward →
        </button>
        
        <button
          @click="navigation.reset()"
          class="btn-secondary text-xs px-3 py-1 ml-auto"
          aria-label="Reset to root"
        >
          Reset
        </button>
      </div>
      
      <!-- Current Position Info -->
      <div class="mt-2 text-xs text-gray-600 dark:text-dark-text-secondary">
        Current position: <strong class="text-gray-900 dark:text-dark-text-primary">{{ navigation.currentPosition.value }}</strong>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useNavigation } from '../composables/useNavigation'
import type { NavigationLevel } from '../composables/useNavigation'

const navigation = useNavigation()

function getChildLabel(child: NavigationLevel): string {
  // Extract the label from the full path (e.g., 'PrismQ.Idea' -> 'Idea')
  const parts = child.split('.')
  return parts[parts.length - 1]
}
</script>
