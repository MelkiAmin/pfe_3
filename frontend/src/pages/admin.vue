<script setup lang="ts">
definePage({
  meta: {
    roles: ['admin'],
  },
})
</script>

<template>
  <div class="admin-page">
    <RouterView />
  </div>
</template>

<style scoped>
.admin-page {
  min-height: 100vh;
}
</style>
