<script setup lang="ts">
const route = useRoute()

const items = [
  { to: '/', icon: 'tabler-home', label: 'Home' },
  { to: '/events', icon: 'tabler-calendar-event', label: 'Events' },
  { to: '/wallet', icon: 'tabler-wallet', label: 'Wallet' },
  { to: '/organizer/dashboard', icon: 'tabler-chart-bar', label: 'Stats' },
]
</script>

<template>
  <VSheet
    class="mobile-bottom-nav d-md-none"
    color="surface"
    border
    elevation="8"
  >
    <VBtn
      v-for="item in items"
      :key="item.to"
      class="mobile-bottom-nav__item"
      :to="item.to"
      :active="route.path.startsWith(item.to)"
      variant="text"
    >
      <VIcon :icon="item.icon" />
      <span>{{ item.label }}</span>
    </VBtn>
  </VSheet>
</template>

<style scoped lang="scss">
.mobile-bottom-nav {
  position: fixed;
  z-index: 1006;
  right: 0;
  bottom: 0;
  left: 0;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  padding: 8px 12px calc(8px + env(safe-area-inset-bottom));
}

.mobile-bottom-nav__item {
  min-width: 0;
  min-height: 56px;
  border-radius: 16px;
  flex-direction: column;
  gap: 4px;
}
</style>
