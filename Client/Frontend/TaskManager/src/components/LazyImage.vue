<template>
  <img
    ref="elementRef"
    :src="currentSrc"
    :alt="alt"
    :width="width"
    :height="height"
    :class="imageClass"
    :loading="nativeLazy ? 'lazy' : undefined"
    @load="onLoad"
    @error="onError"
  />
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useLazyLoad } from '@/composables/useIntersectionObserver'

interface Props {
  src: string
  alt: string
  placeholder?: string
  width?: number | string
  height?: number | string
  nativeLazy?: boolean
  rootMargin?: string
  threshold?: number
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"%3E%3Crect fill="%23f0f0f0" width="100" height="100"/%3E%3C/svg%3E',
  nativeLazy: true,
  rootMargin: '50px',
  threshold: 0.01
})

const emit = defineEmits<{
  load: []
  error: [error: Event]
}>()

const { elementRef, shouldLoad } = useLazyLoad({
  rootMargin: props.rootMargin,
  threshold: props.threshold
})

const isLoaded = ref(false)
const hasError = ref(false)

const currentSrc = computed(() => {
  if (hasError.value) {
    return props.placeholder
  }
  return shouldLoad.value ? props.src : props.placeholder
})

const imageClass = computed(() => {
  return {
    'lazy-image': true,
    'lazy-image--loading': shouldLoad.value && !isLoaded.value,
    'lazy-image--loaded': isLoaded.value,
    'lazy-image--error': hasError.value
  }
})

function onLoad() {
  isLoaded.value = true
  emit('load')
}

function onError(error: Event) {
  hasError.value = true
  emit('error', error)
}
</script>

<style scoped>
.lazy-image {
  transition: opacity 0.3s ease-in-out;
}

.lazy-image--loading {
  opacity: 0.5;
}

.lazy-image--loaded {
  opacity: 1;
}

.lazy-image--error {
  opacity: 0.3;
}
</style>
