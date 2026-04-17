<script setup lang="ts">
import { eventsApi } from '@/services/api'
import type { Category, EventType } from '@/services/api'

definePage({
  meta: {
    layout: 'default',
  },
})

const router = useRouter()
const isSubmitting = ref(false)
const errorMessage = ref('')
const categories = ref<Category[]>([])

const form = reactive({
  title: '',
  description: '',
  category: '',
  eventType: 'in_person' as EventType,
  status: 'draft',
  venueName: '',
  address: '',
  city: '',
  country: '',
  onlineUrl: '',
  startDate: '',
  endDate: '',
  maxCapacity: '',
  isFree: false,
})

const eventTypeItems = [
  { title: 'In person', value: 'in_person' },
  { title: 'Online', value: 'online' },
  { title: 'Hybrid', value: 'hybrid' },
]

const eventStatusItems = [
  { title: 'Draft', value: 'draft' },
  { title: 'Published', value: 'published' },
  { title: 'Cancelled', value: 'cancelled' },
  { title: 'Completed', value: 'completed' },
]

const parseErrorMessage = (error: unknown) => {
  if (!(error instanceof Error))
    return 'Unable to create event. Please try again.'

  const maybeData = error as Error & { data?: Record<string, unknown> }
  const detail = maybeData.data?.detail
  if (typeof detail === 'string')
    return detail

  if (maybeData.data && typeof maybeData.data === 'object') {
    const first = Object.values(maybeData.data)[0]
    if (typeof first === 'string')
      return first
    if (Array.isArray(first) && typeof first[0] === 'string')
      return first[0]
  }

  return error.message || 'Unable to create event. Please try again.'
}

const loadCategories = async () => {
  try {
    categories.value = await eventsApi.listCategories()
  }
  catch {
    categories.value = []
  }
}

const createEvent = async () => {
  errorMessage.value = ''
  isSubmitting.value = true

  try {
    await eventsApi.create({
      title: form.title,
      description: form.description,
      category: form.category ? Number(form.category) : null,
      event_type: form.eventType,
      status: form.status as 'draft' | 'published' | 'cancelled' | 'completed',
      venue_name: form.venueName,
      address: form.address,
      city: form.city,
      country: form.country,
      online_url: form.onlineUrl,
      start_date: form.startDate,
      end_date: form.endDate,
      max_capacity: form.maxCapacity ? Number(form.maxCapacity) : null,
      is_free: form.isFree,
    })

    await router.replace('/events?created=1')
  }
  catch (error: unknown) {
    errorMessage.value = parseErrorMessage(error)
  }
  finally {
    isSubmitting.value = false
  }
}

onMounted(loadCategories)
</script>

<template>
  <div>
    <div class="d-flex flex-wrap align-center justify-space-between gap-4 mb-6">
      <div>
        <h3 class="text-h3 mb-1">
          Create Event
        </h3>
        <p class="text-medium-emphasis mb-0">
          Publish a new event to your catalog.
        </p>
      </div>

      <VBtn
        variant="text"
        to="/events"
        prepend-icon="tabler-arrow-left"
      >
        Back to Events
      </VBtn>
    </div>

    <VCard>
      <VCardText class="pa-6 pa-md-8">
        <VAlert
          v-if="errorMessage"
          type="error"
          variant="tonal"
          class="mb-6"
        >
          {{ errorMessage }}
        </VAlert>

        <VForm @submit.prevent="createEvent">
          <VRow>
            <VCol
              cols="12"
              md="8"
            >
              <AppTextField
                v-model="form.title"
                label="Event title"
                placeholder="Planova Summit 2026"
                required
              />
            </VCol>

            <VCol
              cols="12"
              md="4"
            >
              <AppSelect
                v-model="form.category"
                label="Category"
                :items="[
                  { title: 'No category', value: '' },
                  ...categories.map(category => ({ title: category.name, value: String(category.id) })),
                ]"
              />
            </VCol>

            <VCol cols="12">
              <AppTextarea
                v-model="form.description"
                label="Description"
                placeholder="Tell attendees what this event is about..."
                rows="4"
                required
              />
            </VCol>

            <VCol
              cols="12"
              md="3"
            >
              <AppSelect
                v-model="form.eventType"
                label="Event type"
                :items="eventTypeItems"
              />
            </VCol>

            <VCol
              cols="12"
              md="3"
            >
              <AppSelect
                v-model="form.status"
                label="Status"
                :items="eventStatusItems"
              />
            </VCol>

            <VCol
              cols="12"
              md="3"
            >
              <AppTextField
                v-model="form.startDate"
                label="Start date"
                type="datetime-local"
                required
              />
            </VCol>

            <VCol
              cols="12"
              md="3"
            >
              <AppTextField
                v-model="form.endDate"
                label="End date"
                type="datetime-local"
                required
              />
            </VCol>

            <VCol
              cols="12"
              md="4"
            >
              <AppTextField
                v-model="form.venueName"
                label="Venue name"
                placeholder="Grand Hall"
              />
            </VCol>

            <VCol
              cols="12"
              md="4"
            >
              <AppTextField
                v-model="form.city"
                label="City"
                placeholder="San Francisco"
              />
            </VCol>

            <VCol
              cols="12"
              md="4"
            >
              <AppTextField
                v-model="form.country"
                label="Country"
                placeholder="United States"
              />
            </VCol>

            <VCol cols="12">
              <AppTextField
                v-model="form.address"
                label="Address"
                placeholder="123 Main Street"
              />
            </VCol>

            <VCol
              cols="12"
              md="6"
            >
              <AppTextField
                v-model="form.onlineUrl"
                label="Online URL (optional)"
                placeholder="https://meet.example.com/event"
              />
            </VCol>

            <VCol
              cols="12"
              md="3"
            >
              <AppTextField
                v-model="form.maxCapacity"
                label="Max capacity"
                type="number"
                min="1"
                placeholder="500"
              />
            </VCol>

            <VCol
              cols="12"
              md="3"
              class="d-flex align-end"
            >
              <VCheckbox
                v-model="form.isFree"
                label="Free event"
              />
            </VCol>

            <VCol cols="12">
              <div class="d-flex flex-wrap gap-3">
                <VBtn
                  color="primary"
                  type="submit"
                  :loading="isSubmitting"
                >
                  Create Event
                </VBtn>
                <VBtn
                  variant="tonal"
                  to="/events"
                >
                  Cancel
                </VBtn>
              </div>
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
    </VCard>
  </div>
</template>
