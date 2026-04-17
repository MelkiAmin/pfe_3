<script setup lang="ts">
const props = defineProps<{
  src?: string | null
  alt?: string
  height?: number | string
  width?: number | string
  cover?: boolean
}>()

const root = ref<HTMLElement | null>(null)
const isVisible = ref(false)
const isLoaded = ref(false)
const hasError = ref(false)

onMounted(() => {
  if (!root.value)
    return

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        isVisible.value = true
        observer.disconnect()
      }
    })
  }, { threshold: 0.1 })

  observer.observe(root.value)
})
</script>

<template>
  <div
    ref="root"
    class="lazy-image"
    :style="{ height: typeof height === 'number' ? `${height}px` : height, width: typeof width === 'number' ? `${width}px` : width }"
  >
    <VSkeletonLoader
      v-if="!isLoaded && !hasError"
      type="image"
      class="h-100 w-100"
    />

    <img
      v-if="isVisible && src && !hasError"
      :src="src"
      :alt="alt || 'image'"
      :class="{ loaded: isLoaded, cover: cover !== false }"
      @load="isLoaded = true"
      @error="hasError = true"
    >

    <div
      v-if="hasError"
      class="fallback"
    >
      <VIcon icon="tabler-photo-off" />
    </div>
  </div>
</template>

<style scoped>
.lazy-image {
  position: relative;
  overflow: hidden;
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}

img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  opacity: 0;
  transition: opacity .25s ease;
}

img.cover {
  object-fit: cover;
}

img.loaded {
  opacity: 1;
}

.fallback {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: rgb(var(--v-theme-on-surface-variant));
}
</style>
