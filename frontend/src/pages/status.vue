<script setup lang="ts">
import { eventsApi } from '@/services/api'
import { apiClient } from '@/services/http/axios'
import type { EventListItem } from '@/services/api'
import EventForm from '@/components/events/EventForm.vue'
import { useAuthStore } from '@/stores/auth'

definePage({
  meta: {
    layout: 'default',
    roles: ['organizer', 'admin'],
  },
})

const authStore = useAuthStore()
const loading = ref(true)
const events = ref<EventListItem[]>([])
const eventForm = ref<typeof EventForm | null>(null)
const statusCounts = ref({ pending_count: 0, approved_count: 0, rejected_count: 0 })

const isOrganizer = computed(() => authStore.role === 'organizer')
const isAdmin = computed(() => authStore.role === 'admin')

const statusCards = computed(() => [
  { title: 'En attente', value: statusCounts.value.pending_count, color: 'warning', icon: 'tabler-clock' },
  { title: 'Approuvés', value: statusCounts.value.approved_count, color: 'success', icon: 'tabler-check' },
  { title: 'Rejetés', value: statusCounts.value.rejected_count, color: 'error', icon: 'tabler-x' },
])

const load = async () => {
  loading.value = true
  try {
    console.log('=== LOAD STATUS PAGE ===')
    console.log('User role:', authStore.role)
    console.log('isAdmin:', isAdmin.value)
    console.log('isOrganizer:', isOrganizer.value)
    
    console.log('Fetching status summary from /events/status-summary/...')
    const countsRes = await apiClient.get('/events/status-summary/')
    console.log('Status summary response:', JSON.stringify(countsRes.data))
    
    if (countsRes.data) {
      statusCounts.value = {
        pending_count: Number(countsRes.data.pending_count) || 0,
        approved_count: Number(countsRes.data.approved_count) || 0,
        rejected_count: Number(countsRes.data.rejected_count) || 0,
      }
    }
    console.log('Updated statusCounts:', statusCounts.value)
    
    let eventsEndpoint = isAdmin.value ? '/admin-panel/events/' : '/events/my-events/'
    console.log('Fetching events from:', eventsEndpoint)
    
    const eventsRes = await apiClient.get(eventsEndpoint)
    console.log('Events response status:', eventsRes.status)
    console.log('Events response keys:', eventsRes.data ? Object.keys(eventsRes.data) : 'no data')
    
    const eventsData = eventsRes.data
    if (eventsData) {
      if (eventsData.results) {
        events.value = eventsData.results
        console.log('Paginated - results length:', eventsData.results.length)
      } else if (Array.isArray(eventsData)) {
        events.value = eventsData
        console.log('Array - length:', eventsData.length)
      } else {
        events.value = []
        console.log('Unexpected event data format:', eventsData)
      }
    } else {
      events.value = []
    }
    
    console.log('Final events value:', events.value.length, 'events')
    if (events.value.length > 0) {
      console.log('First event:', JSON.stringify(events.value[0]))
    }
  }
catch (error: any) {
    console.error('[LoadStatus] Error response:', error.response?.data)
    const backendDetail = error.response?.data?.detail
    errorMessage.value = backendDetail || 'Impossible de charger les evenements.'
  }
  finally {
    loading.value = false
  }
}

const handleEventCreated = (newEvent: EventListItem) => {
  load()
}

const refreshCounts = async () => {
  try {
    const countsRes = await apiClient.get('/events/status-summary/')
    statusCounts.value = countsRes.data
  }
  catch (error) {
    console.error('Failed to refresh counts:', error)
  }
}

onMounted(load)
</script>

<template>
  <div class="page-shell">
    <section class="page-hero">
      <div class="hero-content">
        <div class="hero-text">
          <p class="page-kicker">
            Tableau de bord
          </p>
          <h1 class="text-h3 mb-2">
            Gérez vos événements
          </h1>
          <p class="text-medium-emphasis mb-0">
            Suivez le statut de vos événements : en attente, approuvés ou rejetés
          </p>
        </div>
        <div v-if="isOrganizer" class="hero-actions">
          <VBtn
            color="primary"
            size="large"
            rounded="pill"
            class="add-event-btn"
            @click="eventForm?.open()"
          >
            <VIcon icon="tabler-plus" class="mr-2" />
            Ajouter un événement
          </VBtn>
        </div>
      </div>
    </section>

    <VRow>
      <VCol
        v-for="card in statusCards"
        :key="card.title"
        cols="12"
        md="4"
      >
        <VCard class="metric-card">
          <VCardText class="pa-6">
            <div class="metric-header">
              <VChip :color="card.color" variant="tonal" size="small">
                <VIcon :icon="card.icon" size="14" class="mr-1" />
                {{ card.title }}
              </VChip>
            </div>
            <div class="metric-value">
              {{ loading ? '...' : card.value }}
            </div>
            <div class="metric-label">
              {{ card.title.toLowerCase() }}
            </div>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>

    <VCard class="section-card">
      <VCardText class="pa-6 pa-md-8">
        <div class="table-header">
          <h2 class="text-h5 mb-4">Tous les événements</h2>
        </div>

        <VTable v-if="events.length > 0">
          <thead>
            <tr>
              <th>Événement</th>
              <th>Date</th>
              <th>Lieu</th>
              <th>Statut</th>
              <th>Billets</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="event in events" :key="event.id">
              <td>
                <div class="event-cell">
                  <VAvatar
                    v-if="event.cover_image"
                    size="40"
                    rounded="lg"
                  >
                    <VImg :src="event.cover_image" />
                  </VAvatar>
                  <VAvatar v-else size="40" rounded="lg" color="primary">
                    <VIcon icon="tabler-ticket" />
                  </VAvatar>
                  <span class="event-title">{{ event.title }}</span>
                </div>
              </td>
              <td>
                {{ new Date(event.start_date).toLocaleDateString('fr-FR') }}
              </td>
              <td>
                {{ event.city || 'En ligne' }}
              </td>
              <td>
                <VChip
                  :color="{
                    pending: 'warning',
                    approved: 'success',
                    rejected: 'error',
                  }[event.status] || 'grey'"
                  size="small"
                  variant="tonal"
                >
                  {{ event.status }}
                </VChip>
              </td>
              <td>
                {{ event.tickets_sold || 0 }} / {{ event.max_capacity || '∞' }}
              </td>
            </tr>
          </tbody>
        </VTable>

        <div v-else-if="!loading" class="empty-state">
          <VAvatar color="primary" variant="tonal" size="64">
            <VIcon icon="tabler-ticket" size="32" />
          </VAvatar>
          <h3 class="mt-4">Aucun événement</h3>
          <p class="text-medium-emphasis">
            Vous n'avez pas encore créé d'événements
          </p>
          <VBtn
            v-if="isOrganizer"
            color="primary"
            class="mt-4"
            @click="eventForm?.open()"
          >
            <VIcon icon="tabler-plus" class="mr-2" />
            Créer votre premier événement
          </VBtn>
        </div>

        <div v-else class="loading-state">
          <VProgressCircular indeterminate color="primary" />
        </div>
      </VCardText>
    </VCard>

    <EventForm ref="eventForm" @submit="handleEventCreated" />
  </div>
</template>

<style scoped>
.page-shell {
  max-width: 1200px;
  margin: 0 auto;
}

.page-hero {
  margin-bottom: 2rem;
}

.hero-content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.hero-text {
  flex: 1;
  min-width: 280px;
}

.page-kicker {
  font-size: 0.875rem;
  font-weight: 600;
  color: rgb(var(--v-theme-primary));
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.5rem;
}

.hero-actions {
  flex-shrink: 0;
}

.add-event-btn {
  box-shadow: 0 4px 14px rgba(var(--v-theme-primary), 0.3);
}

.add-event-btn:hover {
  box-shadow: 0 6px 20px rgba(var(--v-theme-primary), 0.4);
  transform: translateY(-2px);
}

.metric-card {
  border-radius: 16px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

.metric-header {
  margin-bottom: 0.75rem;
}

.metric-value {
  font-size: 2.5rem;
  font-weight: 800;
  line-height: 1.2;
}

.metric-label {
  font-size: 0.875rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
}

.section-card {
  margin-top: 1.5rem;
  border-radius: 16px;
  overflow: hidden;
}

.event-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.event-title {
  font-weight: 500;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 4rem;
}

@media (max-width: 768px) {
  .hero-content {
    flex-direction: column;
  }

  .hero-actions {
    width: 100%;
  }

  .add-event-btn {
    width: 100%;
  }
}
</style>