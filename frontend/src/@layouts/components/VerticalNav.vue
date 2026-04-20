<script lang="ts" setup>
defineProps<{
  navItems?: unknown[]
  isOverlayNavActive?: boolean
  toggleIsOverlayNavActive?: () => void
}>()
</script>

<template>
  <div class="vertical-nav-shell">
    <slot name="nav-header" />
    <slot name="before-nav-items" />
  </div>
</template>
