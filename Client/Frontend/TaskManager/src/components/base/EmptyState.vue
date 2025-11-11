<template>
  <div class="text-center py-8 px-4" role="status" aria-live="polite">
    <div v-if="icon" class="mb-4 flex justify-center">
      <div class="w-16 h-16 rounded-full bg-gray-100 dark:bg-dark-neutral-subtle flex items-center justify-center">
        <span class="text-3xl" role="img" :aria-label="`Icon: ${icon}`">{{ icon }}</span>
      </div>
    </div>
    <h3 v-if="title" class="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-2">
      {{ title }}
    </h3>
    <p v-if="message" class="text-sm text-gray-500 dark:text-dark-text-secondary mb-4">
      {{ message }}
    </p>
    <slot name="action">
      <button
        v-if="actionText && actionHandler"
        @click="actionHandler"
        :aria-label="actionText"
        class="btn-primary"
      >
        {{ actionText }}
      </button>
    </slot>
  </div>
</template>

<script setup lang="ts">
interface Props {
  icon?: string
  title?: string
  message?: string
  actionText?: string
  actionHandler?: () => void
}

withDefaults(defineProps<Props>(), {
  icon: '📋',
  title: 'No items found',
  message: 'There are no items to display'
})
</script>
