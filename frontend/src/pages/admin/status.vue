<script setup lang="ts">
import { adminPanelApi } from '@/services/api'
import type { EventListItem } from '@/services/api'

definePage({
  meta: {
    layout: 'default',
    roles: ['admin'],
  },
})

const loading = ref(true)
const events = ref<EventListItem[]>([])

const stats = computed(() => ({
  pending: events.value.filter(event => event.status === 'pending').length,
  approved: events.value.filter(event => event.status === 'approved').length,
  rejected: events.value.filter(event => event.status === 'rejected').length,
}))

const load = async () => {
  loading.value = true
  try {
    events.value = await adminPanelApi.listEvents()
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
  <div>
    <h2 class="text-h3 mb-1">
      Validation Status
    </h2>
    <p class="text-medium-emphasis mb-6">
      Follow the current distribution of event approvals across the platform.
    </p>

    <VRow class="mb-6">
      <VCol
        v-for="card in [
          { title: 'Pending', value: stats.pending, color: 'warning' },
          { title: 'Approved', value: stats.approved, color: 'success' },
          { title: 'Rejected', value: stats.rejected, color: 'error' },
        ]"
        :key="card.title"
        cols="12"
        md="4"
      >
        <VCard>
          <VCardText class="pa-6">
            <VChip
              :color="card.color"
              variant="tonal"
              class="mb-3"
            >
              {{ card.title }}
            </VChip>
            <div class="text-h3">
              {{ loading ? '...' : card.value }}
            </div>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>

    <VCard>
      <VCardItem title="Latest event decisions" />
      <VCardText>
        <VSkeletonLoader
          v-if="loading"
          type="table"
        />
        <VTable v-else>
          <thead>
            <tr>
              <th>Event</th>
              <th>Organizer</th>
              <th>Status</th>
              <th>Start date</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="event in events.slice(0, 10)"
              :key="event.id"
            >
              <td>{{ event.title }}</td>
              <td>{{ event.organizer_name }}</td>
              <td>
                <VChip
                  size="small"
                  :color="{ pending: 'warning', approved: 'success', rejected: 'error' }[event.status] || 'default'"
                  variant="tonal"
                >
                  {{ event.status }}
                </VChip>
              </td>
              <td>{{ new Date(event.start_date).toLocaleString() }}</td>
            </tr>
          </tbody>
        </VTable>
      </VCardText>
    </VCard>
  </div>
</template>
