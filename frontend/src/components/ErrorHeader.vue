<script setup lang="ts">
interface Props {
  statusCode?: string | number
  title?: string
  description?: string
}

const props = defineProps<Props>()
</script>

<template>
  <div class="text-center">

