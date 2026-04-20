<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import EventCard from '@/components/events/EventCard.vue'
import { useCatalogStore } from '@/stores/catalog'
import { useAuthStore } from '@/stores/auth'

definePage({
  meta: {
    public: true,
    layout: 'default',
  },
})

const catalogStore = useCatalogStore()
const authStore = useAuthStore()
const { featuredEvents, events, categories, loading, featuredLoading, categoriesLoading } = storeToRefs(catalogStore)

const isLoggedIn = computed(() => authStore.isAuthenticated)
const userRole = computed(() => authStore.role)

const stats = computed(() => {
  const approvedEvents = events.value.filter(event => event.status === 'approved').length

  return [
    { label: 'Evenements', value: approvedEvents, icon: 'tabler-ticket', color: 'primary' },
    { label: 'Categories', value: categories.value.length, icon: 'tabler-category', color: 'info' },
    { label: 'Billets vendus', value: '10K+', icon: 'tabler-users', color: 'success' },
  ]
})

const features = [
  { title: 'Reservation facile', description: 'Reservez vos billets en quelques clics', icon: 'tabler-ticket' },
  { title: 'Evenements exclusifs', description: 'Decouvrez des experiences uniques', icon: 'tabler-star' },
  { title: 'Validation rapide', description: 'Acces instantane aux evenements', icon: 'tabler-check' },
]

onMounted(async () => {
  await Promise.all([
    catalogStore.fetchFeaturedEvents(),
    catalogStore.fetchEvents(),
    catalogStore.fetchCategories(),
  ])
})
</script>

<template>
  <div class="landing-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-bg"></div>
      <div class="container">
        <div class="hero-content">
          <div class="hero-text">
            <VChip color="primary" variant="tonal" class="mb-4">
              Platforme de reservation d'evenements
            </VChip>
            <h1 class="hero-title">
              Decouvrez & reservez vos <span class="text-primary">experiences</span> inoubliables
            </h1>
            <p class="hero-subtitle">
              Planova vous offre une experience de reservation fluide pour les evenements
              les plus marquants. reservez vos places en toute simplicite.
            </p>
            <div class="hero-actions">
              <VBtn
                color="primary"
                size="x-large"
                rounded="pill"
                to="/events"
                class="hero-btn"
              >
                <VIcon icon="tabler-search" class="mr-2" />
                Explorer les evenements
              </VBtn>
              <VBtn
                v-if="!isLoggedIn"
                variant="tonal"
                size="x-large"
                rounded="pill"
                to="/register"
                class="hero-btn"
              >
                <VIcon icon="tabler-user-plus" class="mr-2" />
                Creer un compte
              </VBtn>
            </div>
          </div>
          <div class="hero-stats">
            <div v-for="stat in stats" :key="stat.label" class="stat-item">
              <VIcon :icon="stat.icon" :color="stat.color" size="28" />
              <span class="stat-value">{{ stat.value }}</span>
              <span class="stat-label">{{ stat.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="container">
        <div class="section-header text-center">
          <h2 class="text-h3">Pourquoi choisir Planova?</h2>
          <p class="text-medium-emphasis">Une platforme complete pour vos evenements</p>
        </div>
        <VRow>
          <VCol v-for="feature in features" :key="feature.title" cols="12" md="4">
            <VCard class="feature-card h-100">
              <VCardText class="pa-8 text-center">
                <VAvatar :color="'primary'" variant="tonal" size="64" class="mb-4">
                  <VIcon :icon="feature.icon" size="32" />
                </VAvatar>
                <h3 class="text-h5 mb-2">{{ feature.title }}</h3>
                <p class="text-medium-emphasis mb-0">{{ feature.description }}</p>
              </VCardText>
            </VCard>
          </VCol>
        </VRow>
      </div>
    </section>

    <!-- Featured Events -->
    <section v-if="featuredEvents.length > 0" class="featured-section">
      <div class="container">
        <div class="section-header d-flex justify-space-between align-center">
          <div>
            <h2 class="text-h4">Evenements en vedette</h2>
            <p class="text-medium-emphasis mb-0">Les experiences les plus populaires</p>
          </div>
          <VBtn variant="tonal" rounded="pill" to="/events">
            Tout voir
          </VBtn>
        </div>
        <VRow class="mt-6">
          <VCol
            v-for="event in featuredEvents"
            :key="event.id"
            cols="12"
            sm="6"
            lg="4"
          >
            <EventCard :event="event" />
          </VCol>
        </VRow>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="container">
        <VCard class="cta-card">
          <VCardText class="pa-12 text-center">
            <h2 class="text-h3 mb-4">Pret a vivre des experiences incroyables?</h2>
            <p class="text-medium-emphasis mb-6">
              Rejoignez Planova et reservez vos places des maintenant
            </p>
            <div class="d-flex justify-center gap-4 flex-wrap">
              <VBtn color="primary" size="x-large" rounded="pill" to="/register">
                <VIcon icon="tabler-user-plus" class="mr-2" />
                S'inscrire
              </VBtn>
              <VBtn variant="tonal" size="x-large" rounded="pill" to="/events">
                <VIcon icon="tabler-ticket" class="mr-2" />
                Parcourir les evenements
              </VBtn>
            </div>
          </VCardText>
        </VCard>
      </div>
    </section>

    <!-- Footer -->
    <footer class="landing-footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-brand">
            <div class="brand-logo">P</div>
            <span class="brand-name">Planova</span>
          </div>
          <p class="text-medium-emphasis">
            Platforme de reservation d'evenements en Tunisie
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.landing-page {
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* Hero Section */
.hero-section {
  position: relative;
  padding: 6rem 0;
  overflow: hidden;
  background: linear-gradient(135deg, rgb(var(--v-theme-background)) 0%, rgba(var(--v-theme-primary), 0.05) 100%);
}

.hero-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 50%, rgba(var(--v-theme-primary), 0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(var(--v-theme-info), 0.1) 0%, transparent 40%);
  pointer-events: none;
}

.hero-content {
  position: relative;
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 3rem;
  align-items: center;
}

.hero-title {
  font-size: 3rem;
  line-height: 1.2;
  font-weight: 800;
  margin-bottom: 1rem;
}

.hero-subtitle {
  font-size: 1.125rem;
  color: rgba(var(--v-theme-on-surface), 0.7);
  margin-bottom: 2rem;
  max-width: 480px;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.hero-stats {
  display: flex;
  gap: 2rem;
  justify-content: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
}

.stat-label {
  font-size: 0.875rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
}

/* Features */
.features-section {
  padding: 6rem 0;
  background: rgb(var(--v-theme-surface));
}

.section-header {
  margin-bottom: 3rem;
}

/* Featured */
.featured-section {
  padding: 6rem 0;
}

/* CTA */
.cta-section {
  padding: 6rem 0;
}

.cta-card {
  background: linear-gradient(135deg, rgba(var(--v-theme-primary), 0.1) 0%, rgba(var(--v-theme-info), 0.05) 100%);
  border: 1px solid rgba(var(--v-theme-primary), 0.2);
}

/* Footer */
.landing-footer {
  padding: 3rem 0;
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.footer-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.brand-logo {
  display: grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 12px;
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)), rgb(var(--v-theme-info)));
  color: white;
  font-weight: 800;
}

.brand-name {
  font-size: 1.25rem;
  font-weight: 700;
}

/* Responsive */
@media (max-width: 960px) {
  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    margin-left: auto;
    margin-right: auto;
  }

  .hero-actions {
    justify-content: center;
  }

  .hero-stats {
    margin-top: 2rem;
  }
}

@media (max-width: 600px) {
  .hero-section {
    padding: 3rem 0;
  }

  .hero-title {
    font-size: 1.75rem;
  }

  .hero-stats {
    flex-wrap: wrap;
    gap: 1.5rem;
  }
}
</style>