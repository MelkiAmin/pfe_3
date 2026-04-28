<script lang="ts" setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const routerKey = computed(() => route.fullPath)
</script>

<template>
  <RouterView :key="routerKey" />
</template>