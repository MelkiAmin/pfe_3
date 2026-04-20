<script setup lang="ts">
import { apiClient } from '@/services/http/axios'

definePage({
  meta: {
    layout: 'default',
    roles: ['organizer', 'admin'],
  },
})

const loading = ref(true)
const errorMessage = ref('')
const stats = ref({
  total_events: 0,
  published_events: 0,
  draft_events: 0,
  cancelled_events: 0,
  total_tickets_sold: 0,
  total_revenue: '0.00',
  avg_fill_rate: 0,
  recent_events: [] as any[],
})

const load = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await apiClient.get('/organizer/dashboard/')
    stats.value = data
  }
  catch (error: any) {
    errorMessage.value = error?.response?.data?.detail || 'Unable to load the organizer dashboard.'
  }
  finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="page-shell">
    <section class="page-hero">
      <p class="page-kicker">
        Organisateur
      </p>
      <h1 class="text-h3 mb-2">
        Manage your created events with clarity
      </h1>
      <p class="text-medium-emphasis mb-0">
        Follow approval states, tickets sold and revenue with color-coded status blocks and a simpler dashboard hierarchy.
      </p>
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
        v-for="card in [
          { title: 'Total events', value: stats.total_events, color: 'primary' },
          { title: 'Approved', value: stats.published_events, color: 'success' },
          { title: 'Pending', value: stats.draft_events, color: 'warning' },
          { title: 'Revenue', value: `${Number(stats.total_revenue).toFixed(2)} EUR`, color: 'info' },
        ]"
        :key="card.title"
        cols="12"
        md="6"
        xl="3"
      >
        <VCard class="metric-card">
          <VCardText class="pa-6">
            <VChip :color="card.color" variant="tonal" class="mb-3">
              {{ card.title }}
            </VChip>
            <div class="text-h4">
              {{ loading ? '...' : card.value }}
            </div>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>

    <VCard class="section-card">
      <VCardText class="pa-6 pa-md-8">
        <div class="d-flex justify-space-between align-center flex-wrap gap-3 mb-6">
          <div>
            <p class="page-kicker mb-2">
              Recent creations
            </p>
            <h2 class="text-h4 mb-0">
              Created events
            </h2>
          </div>
        </div>

        <VTable>
          <thead>
            <tr>
              <th>Event</th>
              <th>Status</th>
              <th>Start date</th>
              <th>Tickets sold</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="4">
                <VSkeletonLoader type="table-row@3" />
              </td>
            </tr>
            <tr v-else-if="!stats.recent_events.length">
              <td colspan="4" class="text-center py-6 text-medium-emphasis">
                No events created yet.
              </td>
            </tr>
            <tr
              v-for="event in stats.recent_events"
              :key="event.id"
            >
              <td class="font-weight-bold">
                {{ event.title }}
              </td>
              <td>
                <VChip
                  size="small"
                  :color="{ approved: 'success', pending: 'warning', rejected: 'error' }[event.status] || 'default'"
                  variant="tonal"
                >
                  {{ event.status }}
                </VChip>
              </td>
              <td>{{ new Date(event.start_date).toLocaleDateString() }}</td>
              <td>{{ event.tickets_sold }}</td>
            </tr>
          </tbody>
        </VTable>
      </VCardText>
    </VCard>
  </div>
</template>
