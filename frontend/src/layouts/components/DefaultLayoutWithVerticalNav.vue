<script lang="ts" setup>
import FloatingCart from '@/components/cart/FloatingCart.vue'
import ChatbotWidget from '@/components/chatbot/ChatbotWidget.vue'
import NavBarNotifications from '@/layouts/components/NavBarNotifications.vue'
import UserProfile from '@/layouts/components/UserProfile.vue'
import { useAuthStore } from '@/stores/auth'

defineProps<{
  navItems?: unknown[]
}>()

const route = useRoute()
const authStore = useAuthStore()

const isHomePage = computed(() => route.path === '/')

const showChatbot = computed(() => {
  return authStore.role === 'attendee' && isHomePage.value
})

const navigationItems = computed(() => {
  const items = []

  if (authStore.isAuthenticated) {
    items.push(
      { title: 'Accueil', to: '/', icon: 'tabler-home' },
      { title: 'Evenements', to: '/events', icon: 'tabler-ticket' },
    )
  } else {
    items.push(
      { title: 'Accueil', to: '/', icon: 'tabler-home' },
      { title: 'Evenements', to: '/events', icon: 'tabler-ticket' },
    )
  }

  if (authStore.role === 'admin') {
    items.push(
      { title: 'Utilisateurs', to: '/admin/users', icon: 'tabler-users' },
      { title: 'Organisateurs', to: '/admin/organizers', icon: 'tabler-building' },
      { title: 'Approbations', to: '/admin/approvals', icon: 'tabler-user-check' },
      { title: 'Evenements', to: '/admin/events', icon: 'tabler-calendar' },
      { title: 'Validations', to: '/admin/validations', icon: 'tabler-checkup-list' },
      { title: 'Statistiques', to: '/admin/status', icon: 'tabler-chart-histogram' },
    )
  }

  if (authStore.role === 'organizer') {
    items.push(
      { title: 'Mon tableau de bord', to: '/status', icon: 'tabler-chart-bar' },
    )
  }

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
              Platforme de reservation d'evenements en Tunisie
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
        <RouterLink
          v-if="!authStore.isAuthenticated"
          to="/login"
          class="login-btn"
        >
          <VIcon
            icon="tabler-login"
            size="18"
          />
          <span>Se connecter</span>
        </RouterLink>

        <VChip
          v-if="authStore.isAuthenticated"
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

    <footer v-if="isHomePage" class="home-footer">
      <div class="footer-content">
        <div class="footer-brand">
          <div class="footer-logo">
            <span class="logo-letter">P</span>
          </div>
          <div class="footer-brand-text">
            <h3>Planova</h3>
            <p>Platforme de reservation d'evenements en Tunisie</p>
          </div>
        </div>

        <div class="footer-sections">
          <div class="footer-section">
            <h4>Contact</h4>
            <p>
              <VIcon icon="tabler-mail" size="16" />
              Email: planova@planova.com
            </p>
            <p>
              <VIcon icon="tabler-phone" size="16" />
              Numero: 71 123 456
            </p>
            <p>
              <VIcon icon="tabler-world" size="16" />
              Website: <a href="http://localhost:5173/" target="_blank">localhost:5173</a>
            </p>
          </div>

          <div class="footer-section">
            <h4>Support</h4>
            <p>
              <VIcon icon="tabler-help-circle" size="16" />
              Aide: contact@planova.com
            </p>
          </div>

          <div v-if="authStore.role === 'attendee'" class="footer-section chatbot-hint">
            <h4>Assistant</h4>
            <p>
              <VIcon icon="tabler-message-circle" size="16" />
              Besoin d'aide ? Utilisez notre chatbot
            </p>
            <p class="hint-subtext">Cliquez sur l'icone en bas a droite</p>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <p>&copy; 2026 Planova Tous droits reserves</p>
      </div>
    </footer>

    <FloatingCart v-if="authStore.role === 'attendee'" />
    <ChatbotWidget v-if="showChatbot" />
  </div>
</template>

<style lang="scss" scoped>
.vertical-layout-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
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
.wallet-link,
.login-btn {
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

.login-btn {
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)), rgb(var(--v-theme-info)));
  color: white;
  font-weight: 600;
  padding: 0.7rem 1.25rem;
  box-shadow: 0 4px 14px rgba(var(--v-theme-primary), 0.3);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--v-theme-primary), 0.4);
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
  flex: 1;
  padding: 1.5rem;
}

.home-footer {
  background: linear-gradient(180deg, rgba(var(--v-theme-surface), 0.95) 0%, rgba(var(--v-theme-surface-variant), 1) 100%);
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  padding: 3rem 2rem 1.5rem;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 3rem;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.footer-logo {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)), rgb(var(--v-theme-info)));
  box-shadow: 0 8px 24px rgba(var(--v-theme-primary), 0.25);
}

.logo-letter {
  color: white;
  font-size: 1.5rem;
  font-weight: 800;
}

.footer-brand-text h3 {
  font-size: 1.25rem;
  font-weight: 800;
  margin: 0;
  letter-spacing: -0.02em;
}

.footer-brand-text p {
  font-size: 0.875rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
  margin: 0.25rem 0 0;
}

.footer-sections {
  display: flex;
  gap: 3rem;
  flex-wrap: wrap;
}

.footer-section {
  min-width: 180px;
}

.footer-section h4 {
  font-size: 0.9rem;
  font-weight: 700;
  margin: 0 0 1rem;
  color: rgba(var(--v-theme-on-surface), 0.9);
}

.footer-section p {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: rgba(var(--v-theme-on-surface), 0.7);
  margin: 0 0 0.5rem;
}

.footer-section a {
  color: rgb(var(--v-theme-primary));
  text-decoration: none;
}

.footer-section a:hover {
  text-decoration: underline;
}

.chatbot-hint {
  background: rgba(var(--v-theme-primary), 0.08);
  padding: 1rem 1.25rem;
  border-radius: 12px;
  border: 1px solid rgba(var(--v-theme-primary), 0.15);
}

.hint-subtext {
  font-size: 0.75rem !important;
  color: rgba(var(--v-theme-on-surface), 0.5) !important;
  margin-top: 0.25rem !important;
}

.footer-bottom {
  max-width: 1200px;
  margin: 2rem auto 0;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  text-align: center;
}

.footer-bottom p {
  font-size: 0.8rem;
  color: rgba(var(--v-theme-on-surface), 0.5);
  margin: 0;
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

  .footer-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .footer-brand {
    justify-content: center;
  }

  .footer-sections {
    justify-content: center;
  }
}

@media (max-width: 600px) {
  .home-footer {
    padding: 2rem 1rem 1rem;
  }

  .footer-sections {
    flex-direction: column;
    gap: 1.5rem;
  }

  .footer-section {
    min-width: 100%;
  }
}
</style>