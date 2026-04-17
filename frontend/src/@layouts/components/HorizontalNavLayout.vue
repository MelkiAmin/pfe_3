<script lang="ts" setup>
import { HorizontalNav } from '@layouts/components'
import type { HorizontalNavItems } from '@layouts/types'

import { useLayoutConfigStore } from '@layouts/stores/config'

defineProps<{
  navItems: HorizontalNavItems
}>()

const configStore = useLayoutConfigStore()
</script>

<template>
  <div
    class="layout-wrapper"
    data-allow-mismatch
    :class="configStore._layoutClasses"
  >
    <div
      class="layout-navbar-and-nav-container"
      :class="configStore.isNavbarBlurEnabled && 'header-blur'"
    >

