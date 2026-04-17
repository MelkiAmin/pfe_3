<script setup lang="ts">
import { fakeEvents } from '@/data/fake-events'
import EventCard from '@/components/events/EventCard.vue'
import { eventsApi } from '@/services/api'
import type { Category, EventListItem } from '@/services/api'

definePage({
  meta: {
    public: true,
    layout: 'default',
  },
})

const isLoading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')
const isUsingFakeData = ref(false)
const categories = ref<Category[]>([])
const events = ref<EventListItem[]>([])
const route = useRoute()
const accessToken = useCookie<string | null>('accessToken')
const favoriteByEventId = ref<Record<number, number>>({})

const filters = reactive({
  search: '',
  city: '',
  status: '',
  category: '',
})

const fetchCategories = async () => {
  try {
    categories.value = await eventsApi.listCategories()
  }
  catch {
    categories.value = []
  }
}

const fetchEvents = async () => {
  isLoading.value = true
  errorMessage.value = ''
  isUsingFakeData.value = false

  try {
    const response = await eventsApi.list({
      search: filters.search || undefined,
      city: filters.city || undefined,
      status: filters.status || undefined,
      category: filters.category ? Number(filters.category) : undefined,
      ordering: '-start_date',
    })

    if (response.length) {
      events.value = response
    }
    else {
      events.value = fakeEvents
      isUsingFakeData.value = true
    }
  }
  catch (error: unknown) {
    errorMessage.value = error instanceof Error ? `${error.message} Showing fake events.` : 'Unable to load events. Showing fake events.'
    events.value = fakeEvents
    isUsingFakeData.value = true
  }
  finally {
    isLoading.value = false
  }
}

const fetchFavorites = async () => {
  if (!accessToken.value) {
    favoriteByEventId.value = {}
    return
  }

  try {
    const favorites = await eventsApi.listFavorites()
    favoriteByEventId.value = favorites.reduce<Record<number, number>>((acc, item) => {
      acc[item.event] = item.id
      return acc
    }, {})
  }
  catch {
    favoriteByEventId.value = {}
  }
}

const toggleFavorite = async (eventId: number) => {
  const favoriteId = favoriteByEventId.value[eventId]

  try {
    if (favoriteId) {
      await eventsApi.removeFavorite(favoriteId)
      delete favoriteByEventId.value[eventId]
      return
    }

    const created = await eventsApi.addFavorite(eventId)
    favoriteByEventId.value[eventId] = created.id
  }
  catch {

  }
}

const clearFilters = async () => {
  filters.search = ''
  filters.city = ''
  filters.status = ''
  filters.category = ''
  await fetchEvents()
}

onMounted(async () => {
  if (route.query.created === '1')
    successMessage.value = 'Event created successfully.'

  await Promise.all([fetchCategories(), fetchEvents()])
})
</script>

<template>
  <div class="events-page">
    <VCard class="mb-6">
      <VCardText class="pa-6 pa-md-8">
        <div class="d-flex flex-wrap justify-space-between align-center gap-4 mb-4">
          <div>
            <h3 class="text-h3 mb-1">
              Events Explorer
            </h3>
            <p class="text-medium-emphasis mb-0">
              Browse and filter live events from the backend.
            </p>
          </div>
          <div class="d-flex flex-wrap gap-2">
            <VBtn
              color="primary"
              prepend-icon="tabler-plus"
              to="/events/create"
            >
              Add Event
            </VBtn>
            <VBtn
              variant="tonal"
              prepend-icon="tabler-refresh"
              :loading="isLoading"
              @click="fetchEvents"
            >
              Refresh
            </VBtn>
          </div>
        </div>

        <VRow>
          <VCol
            cols="12"
            md="4"
          >
            <AppTextField
              v-model="filters.search"
              label="Search"
              placeholder="Title, description, venue..."
            />
          </VCol>

          <VCol
            cols="12"
            md="3"
          >
            <AppTextField
              v-model="filters.city"
              label="City"
              placeholder="New York"
            />
          </VCol>

          <VCol
            cols="12"
            md="2"
          >
            <AppSelect
              v-model="filters.status"
              label="Status"
              :items="[
                { title: 'All', value: '' },
                { title: 'Published', value: 'published' },
                { title: 'Draft', value: 'draft' },
                { title: 'Cancelled', value: 'cancelled' },
                { title: 'Completed', value: 'completed' },
              ]"
            />
          </VCol>

          <VCol
            cols="12"
            md="3"
          >
            <AppSelect
              v-model="filters.category"
              label="Category"
              :items="[
                { title: 'All categories', value: '' },
                ...categories.map(category => ({ title: category.name, value: String(category.id) })),
              ]"
            />
          </VCol>
        </VRow>

        <div class="d-flex flex-wrap gap-2 mt-2">
          <VBtn
            color="primary"
            prepend-icon="tabler-search"
            @click="fetchEvents"
          >
            Apply Filters
          </VBtn>
          <VBtn
            variant="text"
            @click="clearFilters"
          >
            Reset
          </VBtn>
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

    <VAlert
      v-if="isUsingFakeData"
      type="info"
      variant="tonal"
      class="mb-6"
    >
      Fake events are currently displayed for preview.
    </VAlert>

    <VAlert
      v-if="successMessage"
      type="success"
      variant="tonal"
      class="mb-6"
      closable
      @click:close="successMessage = ''"
    >
      {{ successMessage }}
    </VAlert>

    <VRow>
      <VCol
        v-if="isLoading"
        cols="12"
      >
        <VSkeletonLoader type="article@3" />
      </VCol>

      <VCol
        v-for="event in events"
        v-else
        :key="event.id"
        cols="12"
        md="6"
        lg="4"
      >
        <div class="position-relative">
          <EventCard :event="event" />
          <IconBtn
            v-if="accessToken"
            class="favorite-btn"
            @click="toggleFavorite(event.id)"
          >
            <VIcon
              :icon="favoriteByEventId[event.id] ? 'tabler-heart-filled' : 'tabler-heart'"
              :color="favoriteByEventId[event.id] ? 'error' : undefined"
            />
          </IconBtn>
        </div>
      </VCol>
    </VRow>

    <VCard
      v-if="!isLoading && !events.length"
      variant="outlined"
    >
      <VCardText class="pa-8 text-center">
        <VIcon
          icon="tabler-calendar-off"
          size="36"
          class="mb-3"
        />
        <h5 class="text-h5 mb-2">
          No events found
        </h5>
        <p class="text-medium-emphasis mb-0">
          Try changing filters or come back after adding events from backend.
        </p>
      </VCardText>
    </VCard>
  </div>
</template>

<style scoped>
.favorite-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgb(var(--v-theme-surface));
}
</style>
