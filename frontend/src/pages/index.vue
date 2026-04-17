<script setup lang="ts">
import { eventsApi, systemApi } from '@/services/api'
import type { EventListItem } from '@/services/api'

const isLoading = ref(true)
const errorMessage = ref('')
const isTestingApi = ref(false)
const healthStatus = ref<'idle' | 'ok' | 'error'>('idle')
const backendTimestamp = ref('')
const recentEvents = ref<EventListItem[]>([])

const stats = computed(() => {
  const publishedEvents = recentEvents.value.filter(event => event.status === 'published').length
  const freeEvents = recentEvents.value.filter(event => event.is_free).length
  const soldOutEvents = recentEvents.value.filter(event => event.is_sold_out).length

  return [
    { label: 'Total events', value: recentEvents.value.length, icon: 'tabler-calendar-event' },
    { label: 'Published', value: publishedEvents, icon: 'tabler-badge-check' },
    { label: 'Free events', value: freeEvents, icon: 'tabler-ticket' },
    { label: 'Sold out', value: soldOutEvents, icon: 'tabler-ban' },
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

    recentEvents.value = events.slice(0, 5)
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

const runConnectionTest = async () => {
  isTestingApi.value = true

  try {
    const response = await systemApi.health()
    healthStatus.value = response.status === 'ok' ? 'ok' : 'error'
    backendTimestamp.value = response.timestamp
  }
  catch {
    healthStatus.value = 'error'
  }
  finally {
    isTestingApi.value = false
  }
}

onMounted(fetchDashboardData)
</script>

<template>
  <div class="dashboard-page">
    <VCard class="hero-card mb-6 overflow-hidden">
      <VCardText class="pa-8 pa-md-10">
        <div class="d-flex flex-wrap align-center justify-space-between gap-6">
          <div class="hero-copy">
            <p class="text-overline mb-2 text-white">
              PLANOVA CONTROL CENTER
            </p>
            <h2 class="text-h3 text-white mb-2">
              Build, publish, and track events from one place.
            </h2>
            <p class="text-body-1 text-white text-high-emphasis mb-6">
              Your frontend is now fully connected to backend APIs and ready for production workflows.
            </p>
            <div class="d-flex flex-wrap gap-3">
              <VBtn
                color="white"
                variant="flat"
                to="/events"
              >
                Explore Events
              </VBtn>
              <VBtn
                color="white"
                variant="outlined"
                :loading="isTestingApi"
                @click="runConnectionTest"
              >
                Test API Connection
              </VBtn>
            </div>
          </div>

          <div class="status-chip-wrap">
            <VChip
              :color="healthStatus === 'ok' ? 'success' : healthStatus === 'error' ? 'error' : 'default'"
              variant="flat"
              size="large"
            >
              {{ healthStatus === 'ok' ? 'Backend Online' : healthStatus === 'error' ? 'Backend Error' : 'Status Unknown' }}
            </VChip>
            <p class="text-caption text-white mt-2 mb-0">
              {{ backendTimestamp ? `Last sync: ${new Date(backendTimestamp).toLocaleString()}` : 'No successful sync yet.' }}
            </p>
          </div>
        </div>
      </VCardText>
    </VCard>

    <VAlert
      v-if="errorMessage"
      type="error"
      variant="tonal"
      class="mb-6"
    >
      {{ errorMessage }}
    </VAlert>

    <VRow class="mb-2">
      <VCol
        v-for="item in stats"
        :key="item.label"
        cols="12"
        sm="6"
        lg="3"
      >
        <VCard>
          <VCardText class="d-flex align-center justify-space-between">
            <div>
              <p class="text-body-2 text-medium-emphasis mb-1">
                {{ item.label }}
              </p>
              <h4 class="text-h4 mb-0">
                {{ item.value }}
              </h4>
            </div>
            <VAvatar
              color="primary"
              variant="tonal"
            >
              <VIcon :icon="item.icon" />
            </VAvatar>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>

    <VCard>
      <VCardItem>
        <VCardTitle>Recent Events</VCardTitle>
        <template #append>
          <VBtn
            variant="text"
            to="/events"
          >
            View all
          </VBtn>
        </template>
      </VCardItem>

      <VDivider />

      <VCardText>
        <VSkeletonLoader
          v-if="isLoading"
          type="list-item-two-line@4"
        />

        <VList
          v-else-if="recentEvents.length"
          lines="two"
        >
          <VListItem
            v-for="event in recentEvents"
            :key="event.id"
            :title="event.title"
            :subtitle="`${event.city || 'Unknown city'} • ${new Date(event.start_date).toLocaleDateString()}`"
          >
            <template #prepend>
              <VAvatar
                color="secondary"
                variant="tonal"
              >
                <VIcon icon="tabler-calendar-time" />
              </VAvatar>
            </template>

            <template #append>
              <VChip
                size="small"
                :color="event.status === 'published' ? 'success' : event.status === 'draft' ? 'warning' : 'default'"
              >
                {{ event.status }}
              </VChip>
            </template>
          </VListItem>
        </VList>

        <VEmptyState
          v-else
          headline="No events yet"
          text="Create your first event to see data here."
          icon="tabler-calendar-plus"
        />
      </VCardText>
    </VCard>
  </div>
</template>

<style scoped lang="scss">
.dashboard-page {
  .hero-card {
    background:
      radial-gradient(circle at 85% 20%, rgb(255 255 255 / 20%), transparent 35%),
      linear-gradient(135deg, rgb(var(--v-theme-primary)) 0%, rgb(var(--v-theme-info)) 100%);
  }

  .hero-copy {
    max-width: 720px;
  }

  .status-chip-wrap {
    min-width: 220px;
    text-align: end;
  }
}
</style>
