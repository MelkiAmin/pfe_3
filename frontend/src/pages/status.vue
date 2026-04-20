<script setup lang="ts">
import { eventsApi } from '@/services/api'
import type { EventListItem } from '@/services/api'

definePage({
  meta: {
    layout: 'default',
    roles: ['organizer', 'admin'],
  },
})

const loading = ref(true)
const events = ref<EventListItem[]>([])

const statusCards = computed(() => ([
  { title: 'Pending', value: events.value.filter(event => event.status === 'pending').length, color: 'warning' },
  { title: 'Approved', value: events.value.filter(event => event.status === 'approved').length, color: 'success' },
  { title: 'Rejected', value: events.value.filter(event => event.status === 'rejected').length, color: 'error' },
]))

const load = async () => {
  loading.value = true
  try {
    events.value = await eventsApi.list()
  }
  catch {
    events.value = []
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
        Status overview
      </p>
      <h1 class="text-h3 mb-2">
        Follow pending, approved and rejected events
      </h1>
      <p class="text-medium-emphasis mb-0">
        A cleaner status board for organisateurs to understand what is live, what is under review and what needs fixes.
      </p>
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
            <VChip :color="card.color" variant="tonal" class="mb-3">
              {{ card.title }}
            </VChip>
            <div class="text-h3">
              {{ loading ? '...' : card.value }}
            </div>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>

    <VCard class="section-card">
      <VCardText class="pa-6 pa-md-8">
        <VTable>
          <thead>
            <tr>
              <th>Event</th>
              <th>City</th>
              <th>Status</th>
              <th>Tickets sold</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="event in events"
              :key="event.id"
            >
              <td class="font-weight-bold">
                {{ event.title }}
              </td>
              <td>{{ event.city || 'Online' }}</td>
              <td>
                <VChip
                  size="small"
                  :color="{ pending: 'warning', approved: 'success', rejected: 'error' }[event.status] || 'default'"
                  variant="tonal"
                >
                  {{ event.status }}
                </VChip>
              </td>
              <td>{{ event.tickets_sold }}</td>
            </tr>
          </tbody>
        </VTable>
      </VCardText>
    </VCard>
  </div>
</template>
