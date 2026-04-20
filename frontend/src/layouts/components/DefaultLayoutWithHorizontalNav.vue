<script lang="ts" setup>
defineProps<{
  navItems?: unknown[]
}>()
</script>

<template>
  <div class="default-layout-shell">
    <main class="default-layout-content">
      <slot />
    </main>
  </div>
</template>

<style lang="scss" scoped>
.default-layout-shell {
  min-height: 100vh;
  background: rgb(var(--v-theme-surface));
}

.default-layout-content {
  padding: 1.5rem;
}
</style>
