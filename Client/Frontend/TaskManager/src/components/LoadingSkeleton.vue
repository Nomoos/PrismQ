<template>
  <div
    :class="['skeleton', `skeleton--${variant}`, { 'skeleton--animated': animated }]"
    :style="style"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed, type CSSProperties } from 'vue'

interface Props {
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'text',
  animated: true
})

const style = computed<CSSProperties>(() => ({
  width: typeof props.width === 'number' ? `${props.width}px` : props.width,
  height: typeof props.height === 'number' ? `${props.height}px` : props.height
}))
</script>

<style scoped>
.skeleton {
  background-color: #e0e0e0;
  display: inline-block;
}

.skeleton--animated {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton--text {
  height: 1em;
  margin-bottom: 0.5em;
  border-radius: 4px;
  transform-origin: 0 60%;
  transform: scale(1, 0.6);
}

.skeleton--circular {
  border-radius: 50%;
}

.skeleton--rectangular {
  border-radius: 4px;
}

@keyframes skeleton-pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
  100% {
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton--animated {
    animation: none;
  }
}
</style>
