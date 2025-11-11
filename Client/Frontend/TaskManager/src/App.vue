<template>
  <div id="app" class="dark min-h-screen bg-gray-50 dark:bg-dark-canvas-default">
    <!-- Skip to main content link for keyboard navigation -->
    <a href="#main-content" class="skip-link">Skip to main content</a>
    
    <RouterView />
    <ToastContainer />
    
    <!-- Screen reader live region for announcements -->
    <div
      role="status"
      aria-live="polite"
      aria-atomic="true"
      class="sr-only"
    >
      {{ announcement }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import ToastContainer from './components/base/ToastContainer.vue'
import { useAccessibility } from './composables/useAccessibility'

const { announcement } = useAccessibility()
</script>

<style>
@import './styles/accessibility.css';
</style>
