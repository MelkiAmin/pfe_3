<script lang="ts" setup>
import FloatingCart from '@/components/cart/FloatingCart.vue'
import NavBarNotifications from '@/layouts/components/NavBarNotifications.vue'
import UserProfile from '@/layouts/components/UserProfile.vue'
import { useAuthStore } from '@/stores/auth'

defineProps<{
  navItems?: unknown[]
}>()

const route = useRoute()
const authStore = useAuthStore()

const navigationItems = computed(() => {
  const items = [
    { title: 'Dashboard', to: '/', icon: 'tabler-layout-dashboard' },
    { title: 'Events', to: '/events', icon: 'tabler-ticket' },
    { title: 'History', to: '/history', icon: 'tabler-history' },
  ]

  if (authStore.role === 'admin')
    items.push({ title: 'Validation', to: '/admin/validations', icon: 'tabler-checkup-list' }, { title: 'Status', to: '/admin/status', icon: 'tabler-chart-histogram' })

  if (authStore.role === 'organizer')
    items.push({ title: 'Status', to: '/status', icon: 'tabler-chart-bar' })

  return items
})

const isActive = (path: string) => {
  if (path === '/')
    return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<template>
  <div class="vertical-layout-shell">
    <header class="topbar">
      <div class="topbar__brand">
        <RouterLink
          to="/"
          class="brand-link"
        >
          <div class="topbar__logo">
            P
          </div>
          <div>
            <div class="topbar__title">
              Planova
            </div>
            <div class="topbar__subtitle">
              Event ticket booking platform
            </div>
          </div>
        </RouterLink>
      </div>

      <nav class="topbar__nav">
        <RouterLink
          v-for="item in navigationItems"
          :key="item.to"
          :to="item.to"
          class="nav-pill"
          :class="{ 'nav-pill--active': isActive(item.to) }"
        >
          <VIcon
            :icon="item.icon"
            size="18"
          />
          <span>{{ item.title }}</span>
        </RouterLink>
      </nav>

      <div class="topbar__actions">
        <VChip
          class="role-chip"
          color="primary"
          variant="flat"
        >
          {{ authStore.roleLabel() }}
        </VChip>

        <RouterLink
          v-if="authStore.role === 'attendee'"
          to="/wallet"
          class="wallet-link"
        >
          <VIcon
            icon="tabler-wallet"
            size="18"
          />
          <span>Wallet</span>
        </RouterLink>

        <NavBarNotifications v-if="authStore.isAuthenticated" />
        <UserProfile v-if="authStore.isAuthenticated" />
      </div>
    </header>

    <main class="vertical-layout-content">
      <slot />
    </main>

    <FloatingCart v-if="authStore.role === 'attendee'" />
  </div>
</template>

<style lang="scss" scoped>
.vertical-layout-shell {
  min-height: 100vh;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.5rem;
  backdrop-filter: blur(18px);
  background: rgba(var(--v-theme-surface), 0.78);
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.brand-link,
.topbar__actions {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  color: inherit;
  text-decoration: none;
}

.topbar__logo {
  display: grid;
  place-items: center;
  inline-size: 3rem;
  block-size: 3rem;
  border-radius: 22px;
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)), rgb(var(--v-theme-info)));
  color: white;
  font-size: 1.15rem;
  font-weight: 800;
  box-shadow: 0 14px 30px rgba(15, 118, 110, 0.28);
}

.topbar__title {
  font-size: 1.05rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.topbar__subtitle {
  font-size: 0.84rem;
  color: rgba(var(--v-theme-on-surface), 0.62);
}

.topbar__nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.nav-pill,
.wallet-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.78rem 1rem;
  border: 1px solid transparent;
  border-radius: 999px;
  color: rgba(var(--v-theme-on-surface), 0.74);
  text-decoration: none;
  transition: all 0.2s ease;
}

.nav-pill:hover,
.wallet-link:hover,
.nav-pill--active {
  color: rgb(var(--v-theme-primary));
  border-color: rgba(var(--v-theme-primary), 0.12);
  background: rgba(var(--v-theme-primary), 0.08);
}

.role-chip {
  font-weight: 700;
  letter-spacing: 0.01em;
}

.vertical-layout-content {
  padding: 1.5rem;
}

@media (max-width: 1120px) {
  .topbar {
    flex-direction: column;
    align-items: stretch;
  }

  .topbar__nav,
  .topbar__actions {
    justify-content: center;
  }

  .brand-link {
    justify-content: center;
  }
}
</style>
