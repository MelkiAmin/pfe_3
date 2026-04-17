<script lang="ts" setup>
import navItems from '@/navigation/vertical'
import { themeConfig } from '@themeConfig'

import Footer from '@/layouts/components/Footer.vue'
import NavbarThemeSwitcher from '@/layouts/components/NavbarThemeSwitcher.vue'
import UserProfile from '@/layouts/components/UserProfile.vue'
import FloatingCart from '@/components/cart/FloatingCart.vue'
import MobileBottomNav from '@/components/navigation/MobileBottomNav.vue'
import NavBarI18n from '@core/components/I18n.vue'

import { VerticalNavLayout } from '@layouts'
</script>

<template>
  <VerticalNavLayout :nav-items="navItems">

