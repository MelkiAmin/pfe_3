<script setup lang="ts">
import DefaultLayoutWithVerticalNav from '@/layouts/components/DefaultLayoutWithVerticalNav.vue'

definePage({
  meta: {
    layout: 'blank',
    roles: ['admin'],
  },
})
</script>

<template>
  <DefaultLayoutWithVerticalNav>
    <RouterView />
  </DefaultLayoutWithVerticalNav>
</template>
