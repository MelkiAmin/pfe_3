<script lang="ts" setup>
import AppLoadingIndicator from '@/components/AppLoadingIndicator.vue'

type LoadingIndicatorHandle = {
  fallbackHandle: () => void
  resolveHandle: () => void
}

const { injectSkinClasses } = useSkins()

injectSkinClasses()

const isFallbackStateActive = ref(false)
const refLoadingIndicator = ref<LoadingIndicatorHandle | null>(null)

watch([isFallbackStateActive, refLoadingIndicator], () => {
  const indicator = refLoadingIndicator.value

  if (isFallbackStateActive.value) {
    indicator?.fallbackHandle?.()
    return
  }

  indicator?.resolveHandle?.()
}, { immediate: true })

</script>

<template>
  <AppLoadingIndicator ref="refLoadingIndicator" />

  <div
    class="layout-wrapper layout-blank"
    data-allow-mismatch
  >
    <RouterView #="{Component}">
      <Suspense
        :timeout="0"
        @fallback="isFallbackStateActive = true"
        @resolve="isFallbackStateActive = false"
      >
        <Component :is="Component" />
      </Suspense>
    </RouterView>
  </div>
</template>

<style>
.layout-wrapper.layout-blank {
  flex-direction: column;
}
</style>
