<script setup lang="ts">
import AppSelect from '@/@core/components/app-form-elements/AppSelect.vue'
import AppTextField from '@/@core/components/app-form-elements/AppTextField.vue'
import AppTextarea from '@/@core/components/app-form-elements/AppTextarea.vue'
import { eventsApi } from '@/services/api'
import type { Category, EventType } from '@/services/api'

definePage({
  meta: {
    layout: 'default',
    roles: ['organizer'],
  },
})

const router = useRouter()
const isSubmitting = ref(false)
const errorMessage = ref('')
const categories = ref<Category[]>([])
const coverPreview = ref('')
const formRef = ref()

const form = reactive({
  title: '',
  description: '',
  category: '',
  eventType: 'in_person' as EventType,
  venueName: '',
  address: '',
  city: '',
  country: '',
  onlineUrl: '',
  startDate: '',
  endDate: '',
  maxCapacity: '',
  ticketPrice: '',
  ticketQuantity: '',
  isFree: false,
  coverImage: null as File | null,
})

const requiredRule = (value: unknown) => {
  if (typeof value === 'number')
    return Number.isFinite(value) || 'This field is required.'

  return (value !== null && value !== undefined && String(value).trim().length > 0) || 'This field is required.'
}

const positivePriceRule = (value: unknown) => {
  if (value === null || value === undefined || value === '')
    return 'This field is required.'

  return Number(value) >= 0 || 'Ticket price must be 0 or more.'
}

const quantityRule = (value: unknown) => {
  if (value === null || value === undefined || value === '')
    return 'This field is required.'

  return Number(value) > 0 || 'Number of tickets must be at least 1.'
}

const fileRequiredRule = (value: unknown) => {
  const picked = Array.isArray(value) ? value[0] : value
  return Boolean(picked) || 'Cover image is required.'
}

const isSubmitDisabled = computed(() => (
  isSubmitting.value
  || !form.title.trim()
  || !form.description.trim()
  || !form.coverImage
  || form.ticketPrice === ''
  || Number(form.ticketPrice) < 0
  || form.ticketQuantity === ''
  || Number(form.ticketQuantity) < 1
  || !form.startDate
  || !form.endDate
))

const eventTypeItems = [
  { title: 'In person', value: 'in_person' },
  { title: 'Online', value: 'online' },
  { title: 'Hybrid', value: 'hybrid' },
]

const parseErrorMessage = (error: unknown) => {
  if (!(error instanceof Error))
    return 'Unable to create event. Please try again.'

  const maybeData = error as Error & { data?: Record<string, unknown> }
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
  categories.value = [
    { id: 1, name: 'Technologie', slug: 'technologie', description: '', icon: 'tabler-code' },
    { id: 2, name: 'Sport', slug: 'sport', description: '', icon: 'tabler-ball' },
    { id: 3, name: 'Musique', slug: 'musique', description: '', icon: 'tabler-music' },
    { id: 4, name: 'Éducation', slug: 'education', description: '', icon: 'tabler-school' },
    { id: 5, name: 'Business', slug: 'business', description: '', icon: 'tabler-briefcase' },
    { id: 6, name: 'Culture', slug: 'culture', description: '', icon: 'tabler-artboard' },
    { id: 7, name: 'Santé', slug: 'sante', description: '', icon: 'tabler-heart' },
    { id: 8, name: 'Gaming', slug: 'gaming', description: '', icon: 'tabler-gamepad' },
    { id: 9, name: 'Autre', slug: 'autre', description: '', icon: 'tabler-category' },
  ]
}

const onCoverSelected = (files: File[] | File | null) => {
  const picked = Array.isArray(files) ? files[0] : files
  form.coverImage = picked || null
  coverPreview.value = picked ? URL.createObjectURL(picked) : ''
}

const createEvent = async () => {
  errorMessage.value = ''
  const validation = await formRef.value?.validate?.()
  if (validation && !validation.valid)
    return

  isSubmitting.value = true

  try {
    const payload = new FormData()
    payload.append('title', form.title)
    payload.append('description', form.description)
    payload.append('event_type', form.eventType)
    payload.append('start_date', form.startDate)
    payload.append('end_date', form.endDate)
    payload.append('ticket_price', form.ticketPrice)
    payload.append('ticket_quantity', form.ticketQuantity)
    payload.append('is_free', String(form.isFree))

    if (form.category)
      payload.append('category', form.category)
    if (form.coverImage)
      payload.append('cover_image', form.coverImage)
    if (form.venueName)
      payload.append('venue_name', form.venueName)
    if (form.address)
      payload.append('address', form.address)
    if (form.city)
      payload.append('city', form.city)
    if (form.country)
      payload.append('country', form.country)
    if (form.onlineUrl)
      payload.append('online_url', form.onlineUrl)
    if (form.maxCapacity)
      payload.append('max_capacity', form.maxCapacity)

    await eventsApi.create(payload)
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
  <div class="event-create-page">
    <div class="hero-card mb-6">
      <div>
        <h3 class="text-h3 mb-2">
          Soumettre un nouvel événement
        </h3>
        <p class="text-medium-emphasis mb-0">
          Créez une annonce soignée. Chaque soumission est envoyée pour validation admin avant d'être publiée.
        </p>
      </div>

      <VBtn
        variant="text"
        to="/events"
        prepend-icon="tabler-arrow-left"
      >
        Retour aux événements
      </VBtn>
    </div>

    <VCard class="form-card">
      <VCardText class="pa-6 pa-md-8">
        <VAlert
          v-if="errorMessage"
          type="error"
          variant="tonal"
          class="mb-6"
        >
          {{ errorMessage }}
        </VAlert>

        <VForm ref="formRef" @submit.prevent="createEvent">
          <VRow>
            <VCol cols="12" md="8">
              <AppTextField
                v-model="form.title"
                label="Event title"
                placeholder="Planova Summit 2026"
                :rules="[requiredRule]"
                required
              />
            </VCol>

            <VCol cols="12" md="4">
              <AppSelect
                v-model="form.category"
                label="Category"
                :items="[
                  { title: 'No category', value: '' },
                  ...categories.map(category => ({ title: category.name, value: String(category.id) })),
                ]"
              />
            </VCol>

            <VCol cols="12" md="7">
              <AppTextarea
                v-model="form.description"
                label="Description"
                rows="5"
                :rules="[requiredRule]"
                required
              />
            </VCol>

            <VCol cols="12" md="5">
              <VFileInput
                :model-value="form.coverImage"
                accept="image/*"
                label="Cover image"
                prepend-icon="tabler-photo"
                variant="outlined"
                :rules="[fileRequiredRule]"
                required
                @update:model-value="onCoverSelected"
              />

              <VSheet
                class="cover-preview mt-3"
                rounded="xl"
              >
                <VImg
                  v-if="coverPreview"
                  :src="coverPreview"
                  cover
                  height="200"
                />
                <div
                  v-else
                  class="cover-preview__empty"
                >
                  Event cover preview
                </div>
              </VSheet>
            </VCol>

            <VCol cols="12" md="4">
              <AppSelect
                v-model="form.eventType"
                label="Event type"
                :items="eventTypeItems"
              />
            </VCol>

            <VCol cols="12" md="4">
              <AppTextField
                v-model="form.ticketPrice"
                label="Ticket price"
                type="number"
                min="0"
                step="0.01"
                :rules="[positivePriceRule]"
                required
              />
            </VCol>

            <VCol cols="12" md="4">
              <AppTextField
                v-model="form.ticketQuantity"
                label="Number of tickets"
                type="number"
                min="1"
                :rules="[quantityRule]"
                required
              />
            </VCol>

            <VCol cols="12" md="6">
              <AppTextField
                v-model="form.startDate"
                label="Start date"
                type="datetime-local"
                :rules="[requiredRule]"
                required
              />
            </VCol>

            <VCol cols="12" md="6">
              <AppTextField
                v-model="form.endDate"
                label="End date"
                type="datetime-local"
                :rules="[requiredRule]"
                required
              />
            </VCol>

            <VCol cols="12" md="4">
              <AppTextField
                v-model="form.venueName"
                label="Venue name"
              />
            </VCol>

            <VCol cols="12" md="4">
              <AppTextField
                v-model="form.city"
                label="City"
              />
            </VCol>

            <VCol cols="12" md="4">
              <AppTextField
                v-model="form.country"
                label="Country"
              />
            </VCol>

            <VCol cols="12">
              <AppTextField
                v-model="form.address"
                label="Address"
              />
            </VCol>

            <VCol cols="12" md="6">
              <AppTextField
                v-model="form.onlineUrl"
                label="Online URL"
              />
            </VCol>

            <VCol cols="12" md="3">
              <AppTextField
                v-model="form.maxCapacity"
                label="Max capacity"
                type="number"
                min="1"
              />
            </VCol>

            <VCol
              cols="12"
              md="3"
              class="d-flex align-end"
            >
              <VCheckbox
                v-model="form.isFree"
                label="Événement gratuit"
              />
            </VCol>

            <VCol cols="12">
              <div class="d-flex flex-wrap gap-3">
                <VBtn
                  color="primary"
                  type="submit"
                  :disabled="isSubmitDisabled"
                  :loading="isSubmitting"
                >
                  Soumettre pour validation
                </VBtn>
                <VBtn
                  variant="tonal"
                  to="/events"
                >
                  Annuler
                </VBtn>
              </div>
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
    </VCard>
  </div>
</template>

<style scoped>
.hero-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.5rem;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 28px;
  background: linear-gradient(135deg, rgba(var(--v-theme-primary), 0.12), rgba(var(--v-theme-info), 0.08));
}

.form-card {
  border-radius: 28px;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
}

.cover-preview {
  overflow: hidden;
  min-height: 200px;
  border: 1px dashed rgba(var(--v-border-color), var(--v-border-opacity));
}

.cover-preview__empty {
  display: grid;
  place-items: center;
  min-height: 200px;
  color: rgba(var(--v-theme-on-surface), 0.58);
}
</style>
