<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold text-gray-900">PrismQ Web Client</h1>
      </div>
    </header>
    <main>
      <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <router-view />
      </div>
    </main>
    <NotificationToast />
  </div>
</template>

<script setup lang="ts">
import NotificationToast from '@/components/NotificationToast.vue'
</script>

<style scoped>
/* App-specific styles */
</style>
