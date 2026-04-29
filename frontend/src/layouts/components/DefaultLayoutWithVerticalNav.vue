<script lang="ts" setup>
import FloatingCart from '@/components/cart/FloatingCart.vue'
import ChatbotWidget from '@/components/chatbot/ChatbotWidget.vue'
import NavBarNotifications from '@/layouts/components/NavBarNotifications.vue'
import UserProfile from '@/layouts/components/UserProfile.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const isHomePage = computed(() => route.path === '/')

const isEventsPage = computed(() => {
  return route.path?.startsWith('/events') === true
})

const hasToken = computed(() => {
  return Boolean(
    authStore.accessToken ||
    localStorage.getItem('auth_access_token')
  )
})

const userRole = computed(() => {
  if (authStore.role) return authStore.role

  try {
    const userData = localStorage.getItem('auth_user')
    return userData ? JSON.parse(userData)?.role : null
  } catch {
    return null
  }
})

const isAttendee = computed(() => userRole.value === 'attendee')

const showChatbot = computed(() => {
  const isPublicPage = isHomePage.value || isEventsPage.value
  return isPublicPage || isAttendee.value
})

const navigationItems = computed(() => {
  const baseItems = [
    { title: 'Accueil', to: '/', icon: 'tabler-home' },
    { title: 'Événements', to: '/events', icon: 'tabler-calendar' },
  ]

  if (userRole.value === 'admin') {
    return [
      ...baseItems,
      { title: 'Utilisateurs', to: '/admin/users', icon: 'tabler-users' },
      { title: 'Organisateurs', to: '/admin/organizers', icon: 'tabler-user-star' },
      { title: 'Approbations', to: '/admin/approvals', icon: 'tabler-checkup' },
      { title: 'Validations', to: '/admin/events', icon: 'tabler-check' },
      { title: 'Statistiques', to: '/admin/dashboard', icon: 'tabler-chart-bar' },
    ]
  }

  if (userRole.value === 'organizer') {
    return [
      ...baseItems,
      { title: 'Tableau de bord', to: '/organizer/dashboard', icon: 'tabler-layout-dashboard' },
    ]
  }

  return baseItems
})

const isActive = (path: string) => {
  return route.path === path || route.path?.startsWith(path + '/')
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
  padding: 0.75rem 2rem;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.85);
  border-bottom: 1px solid rgba(99, 102, 241, 0.08);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 8px 24px rgba(99, 102, 241, 0.06);
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
  inline-size: 2.75rem;
  block-size: 2.75rem;
  border-radius: 16px;
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  color: white;
  font-size: 1rem;
  font-weight: 800;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}

.topbar__title {
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.topbar__subtitle {
  font-size: 0.8rem;
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.topbar__nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.nav-pill,
.wallet-link,
.login-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.1rem;
  border: 1px solid transparent;
  border-radius: 12px;
  color: rgba(var(--v-theme-on-surface), 0.7);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.login-btn {
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  color: white;
  font-weight: 600;
  padding: 0.6rem 1.25rem;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
  border: none;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.45);
}

.nav-pill:hover,
.wallet-link:hover,
.nav-pill--active {
  color: #6366F1;
  background: rgba(99, 102, 241, 0.12);
  border-color: rgba(99, 102, 241, 0.15);
  font-weight: 600;
}

.role-chip {
  font-weight: 600;
  letter-spacing: 0.02em;
  border-radius: 10px;
}

.vertical-layout-content {
  flex: 1;
  padding: 1.5rem;
}

.home-footer {
  background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
  border-top: 1px solid rgba(99, 102, 241, 0.08);
  padding: 4rem 2rem 1.5rem;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 4rem;
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
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
}

.logo-letter {
  color: white;
  font-size: 1.5rem;
  font-weight: 800;
}

.footer-brand-text h3 {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.footer-brand-text p {
  font-size: 0.875rem;
  color: rgba(var(--v-theme-on-surface), 0.5);
  margin: 0.25rem 0 0;
}

.footer-sections {
  display: flex;
  gap: 4rem;
  flex-wrap: wrap;
}

.footer-section {
  min-width: 180px;
}

.footer-section h4 {
  font-size: 0.85rem;
  font-weight: 700;
  margin: 0 0 1rem;
  color: rgba(var(--v-theme-on-surface), 0.9);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.footer-section p {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
  margin: 0 0 0.75rem;
}

.footer-section a {
  color: #6366F1;
  text-decoration: none;
  font-weight: 500;
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