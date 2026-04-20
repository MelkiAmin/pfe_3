<script setup lang="ts">
import { useAuth } from '@/composables/useAuth'
import LoginRoleForm from '@/components/auth/LoginRoleForm.vue'

definePage({
  meta: {
    layout: 'blank',
    public: true,
  },
})

const { clearSession } = useAuth()

onMounted(() => clearSession())
</script>

<template>
  <div class="auth-screen">
    <div class="auth-screen__side">
      <div class="auth-mark">Planova</div>
      <p class="page-kicker">
        Ticketing made elegant
      </p>
      <h1 class="auth-screen__title">
        Book, validate, and manage memorable events.
      </h1>
      <p class="auth-screen__text">
        A premium reservation experience for admins, organisateurs and attendees, all in one polished workspace.
      </p>

      <div class="feature-list">
        <div class="feature-item">
          <VIcon icon="tabler-check" />
          <span>Instant event validation workflow</span>
        </div>
        <div class="feature-item">
          <VIcon icon="tabler-check" />
          <span>Smart basket and ticket reservation flow</span>
        </div>
        <div class="feature-item">
          <VIcon icon="tabler-check" />
          <span>Professional dashboards for every role</span>
        </div>
      </div>
    </div>

    <div class="auth-screen__form">
      <VCard class="auth-card section-card">
        <VCardText class="pa-8">
          <p class="page-kicker">
            Bon retour
          </p>
          <h2 class="text-h3 mb-2">
            Connectez-vous à Planova
          </h2>
          <p class="text-medium-emphasis mb-6">
            Accédez à vos réservations, validations et événements depuis une interface moderne.
          </p>

          <LoginRoleForm />
        </VCardText>
      </VCard>
    </div>
  </div>
</template>

<style scoped>
.auth-screen {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(var(--v-theme-primary), 0.18), transparent 26%),
    linear-gradient(135deg, #081717 0%, #0f2d2f 52%, #eaf6f2 52%, #f4f7f6 100%);
}

.auth-screen__side,
.auth-screen__form {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.auth-screen__side {
  flex-direction: column;
  align-items: flex-start;
  color: white;
}

.auth-mark {
  display: inline-flex;
  padding: 0.7rem 1rem;
  margin-bottom: 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.auth-screen__title {
  max-width: 520px;
  margin-bottom: 1rem;
  font-size: clamp(2.5rem, 4vw, 4.5rem);
  line-height: 1;
  letter-spacing: -0.04em;
}

.auth-screen__text {
  max-width: 520px;
  font-size: 1.08rem;
  color: rgba(255, 255, 255, 0.8);
}

.feature-list {
  display: grid;
  gap: 0.9rem;
  margin-top: 2rem;
}

.feature-item {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  color: rgba(255, 255, 255, 0.88);
}

.auth-card {
  inline-size: min(520px, 100%);
}

@media (max-width: 960px) {
  .auth-screen {
    grid-template-columns: 1fr;
    background: rgb(var(--v-theme-background));
  }

  .auth-screen__side {
    align-items: center;
    padding-bottom: 0;
    text-align: center;
    color: rgb(var(--v-theme-on-background));
  }

  .auth-screen__text,
  .auth-screen__title {
    max-width: 100%;
  }

  .feature-item {
    color: rgba(var(--v-theme-on-surface), 0.76);
  }
}
</style>
