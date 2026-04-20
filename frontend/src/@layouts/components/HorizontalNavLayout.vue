<script lang="ts" setup>
defineProps<{
  navItems?: unknown[]
}>()
</script>

<template>
  <div class="horizontal-nav-layout">
    <slot />
  </div>
</template>
