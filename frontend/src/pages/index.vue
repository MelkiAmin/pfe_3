<script setup lang="ts">
import { eventsApi, systemApi } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import type { EventListItem } from '@/services/api'

const authStore = useAuthStore()
const isLoading = ref(true)
const errorMessage = ref('')
const healthStatus = ref<'idle' | 'ok' | 'error'>('idle')
const backendTimestamp = ref('')
const recentEvents = ref<EventListItem[]>([])

const stats = computed(() => {
  const approvedEvents = recentEvents.value.filter(event => event.status === 'approved').length
  const soldOutEvents = recentEvents.value.filter(event => event.is_sold_out).length

  return [
    { label: 'Événements visibles', value: recentEvents.value.length, icon: 'tabler-ticket', color: 'primary' },
    { label: 'Approuvés', value: approvedEvents, icon: 'tabler-circle-check', color: 'success' },
    { label: 'Complet', value: soldOutEvents, icon: 'tabler-flame', color: 'warning' },
    { label: 'Rôle actuel', value: authStore.roleLabel(), icon: 'tabler-user-shield', color: 'info' },
  ]
})

const fetchDashboardData = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const [events, health] = await Promise.all([
      eventsApi.list({ ordering: '-created_at' }),
      systemApi.health(),
    ])

    recentEvents.value = events.slice(0, 6)
    healthStatus.value = health.status === 'ok' ? 'ok' : 'error'
    backendTimestamp.value = health.timestamp
  }
  catch (error: unknown) {
    errorMessage.value = error instanceof Error ? error.message : 'Failed to load dashboard data.'
    healthStatus.value = 'error'
  }
  finally {
    isLoading.value = false
  }
}

onMounted(fetchDashboardData)
</script>

<template>
  <div class="page-shell">
    <section class="page-hero dashboard-hero">
      <div class="dashboard-hero__copy">
        <p class="page-kicker">
          Planova dashboard
        </p>
        <h1 class="text-h2 mb-3">
          A professional control room for ticket booking and event validation
        </h1>
        <p class="text-medium-emphasis mb-5">
          Navigate approved events, follow platform activity, and access role-based actions from a cleaner and more modern reservation interface.
        </p>

        <div class="d-flex flex-wrap gap-3">
          <VBtn
            color="primary"
            rounded="pill"
            to="/events"
          >
            Explorer les événements
          </VBtn>
          <VBtn
            variant="tonal"
            rounded="pill"
            to="/history"
          >
            Voir l’historique
          </VBtn>
        </div>
      </div>

      <div class="dashboard-hero__status">
        <div class="status-card">
          <div class="text-medium-emphasis mb-2">
            API status
          </div>
          <VChip
            :color="healthStatus === 'ok' ? 'success' : 'error'"
            variant="flat"
          >
            {{ healthStatus === 'ok' ? 'Online' : 'Offline' }}
          </VChip>
          <div class="text-body-2 text-medium-emphasis mt-4">
            {{ backendTimestamp ? `Last sync: ${new Date(backendTimestamp).toLocaleString()}` : 'No sync yet' }}
          </div>
        </div>
      </div>
    </section>

    <VAlert
      v-if="errorMessage"
      type="error"
      variant="tonal"
    >
      {{ errorMessage }}
    </VAlert>

    <VRow>
      <VCol
        v-for="item in stats"
        :key="item.label"
        cols="12"
        md="6"
        xl="3"
      >
        <VCard class="metric-card">
          <VCardText class="pa-6 d-flex align-center justify-space-between">
            <div>
              <div class="text-medium-emphasis mb-2">
                {{ item.label }}
              </div>
              <div class="text-h4">
                {{ item.value }}
              </div>
            </div>
            <VAvatar
              :color="item.color"
              variant="tonal"
              size="54"
            >
              <VIcon :icon="item.icon" />
            </VAvatar>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>

    <VCard class="section-card">
      <VCardText class="pa-6 pa-md-8">
        <div class="d-flex justify-space-between align-center flex-wrap gap-3 mb-6">
          <div>
            <p class="page-kicker mb-2">
              Latest events
            </p>
            <h2 class="text-h4 mb-0">
              Recently added experiences
            </h2>
          </div>

          <VBtn
            variant="tonal"
            rounded="pill"
            to="/events"
          >
            Tout voir
          </VBtn>
        </div>

        <VRow>
          <VCol
            v-if="isLoading"
            cols="12"
          >
            <VSkeletonLoader type="article@3" />
          </VCol>

          <VCol
            v-for="event in recentEvents"
            v-else
            :key="event.id"
            cols="12"
            md="6"
            xl="4"
          >
            <VSheet class="recent-event-tile">
              <div class="d-flex align-start justify-space-between gap-3 mb-3">
                <div>
                  <div class="font-weight-bold mb-1">
                    {{ event.title }}
                  </div>
                  <div class="text-body-2 text-medium-emphasis">
                    {{ event.city || 'Online' }}
                  </div>
                </div>
                <VChip
                  size="small"
                  :color="event.status === 'approved' ? 'success' : 'warning'"
                  variant="tonal"
                >
                  {{ event.status }}
                </VChip>
              </div>

              <div class="text-body-2 text-medium-emphasis mb-4">
                {{ new Date(event.start_date).toLocaleString() }}
              </div>

              <VBtn
                variant="text"
                :to="`/events/${event.slug}`"
              >
                Consulter
              </VBtn>
            </VSheet>
          </VCol>
        </VRow>
      </VCardText>
    </VCard>
  </div>
</template>

<style scoped>
.dashboard-hero {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 1.5rem;
}

.status-card,
.recent-event-tile {
  padding: 1.2rem;
  border-radius: 24px;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  background: rgba(var(--v-theme-surface), 0.8);
}

@media (max-width: 1200px) {
  .dashboard-hero {
    grid-template-columns: 1fr;
  }
}
</style>
