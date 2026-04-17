<script setup lang="ts">
import AppSearchHeaderBg from '@images/pages/app-search-header-bg.png'

interface Props {
  title?: string
  subtitle?: string
  customClass?: string
  placeholder?: string
  density?: 'comfortable' | 'compact' | 'default'
  isReverse?: boolean
}

defineOptions({
  inheritAttrs: false,
})

const props = withDefaults(defineProps<Props>(), {
  density: 'comfortable',
  isReverse: false,
})
</script>

<template>

