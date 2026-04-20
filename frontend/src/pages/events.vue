<script setup lang="ts">
import AppSelect from '@/@core/components/app-form-elements/AppSelect.vue'
import AppTextField from '@/@core/components/app-form-elements/AppTextField.vue'
import EventCard from '@/components/events/EventCard.vue'
import { eventsApi } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import type { Category, EventListItem } from '@/services/api'

definePage({
  meta: {
    public: true,
    layout: 'default',
  },
})

const authStore = useAuthStore()
const isLoading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')
const categories = ref<Category[]>([])
const events = ref<EventListItem[]>([])
const route = useRoute()

const canCreateEvent = computed(() => ['organizer', 'admin'].includes(authStore.role))

const filters = reactive({
  search: '',
  city: '',
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
  try {
    const response = await eventsApi.list({
      search: filters.search || undefined,
      city: filters.city || undefined,
      category: filters.category ? Number(filters.category) : undefined,
      status: 'approved',
      ordering: '-start_date',
    })
    events.value = response.filter(event => event.status === 'approved')
  }
  catch (error: unknown) {
    errorMessage.value = error instanceof Error ? error.message : 'Unable to load events.'
    events.value = []
  }
  finally {
    isLoading.value = false
  }
}

const clearFilters = async () => {
  filters.search = ''
  filters.city = ''
  filters.category = ''
  await fetchEvents()
}

onMounted(async () => {
  if (route.query.created === '1')
    successMessage.value = 'Votre événement a été envoyé avec succès pour validation.'

  await Promise.all([fetchCategories(), fetchEvents()])
})
</script>

<template>
  <div class="page-shell">
    <section class="page-hero events-hero">
      <div>
        <p class="page-kicker">
          Réservations modernes
        </p>
        <h1 class="text-h2 mb-2">
          Explorez des expériences validées et prêtes à réserver
        </h1>
        <p class="text-medium-emphasis mb-0">
          Une galerie d’événements approuvés, présentés avec une navigation claire, une recherche rapide et un parcours d’achat simple.
        </p>
      </div>

      <div class="d-flex flex-wrap gap-3">
        <VBtn
          v-if="canCreateEvent"
          color="primary"
          prepend-icon="tabler-plus"
          rounded="pill"
          to="/events/create"
        >
          Ajouter un événement
        </VBtn>
        <VBtn
          variant="tonal"
          prepend-icon="tabler-refresh"
          rounded="pill"
          :loading="isLoading"
          @click="fetchEvents"
        >
          Rafraîchir
        </VBtn>
      </div>
    </section>

    <VCard class="section-card">
      <VCardText class="pa-6">
        <VRow>
          <VCol cols="12" md="5">
            <AppTextField
              v-model="filters.search"
              label="Recherche"
              prepend-inner-icon="tabler-search"
              placeholder="Titre, ville, description..."
            />
          </VCol>
          <VCol cols="12" md="3">
            <AppTextField
              v-model="filters.city"
              label="Ville"
              prepend-inner-icon="tabler-map-pin"
              placeholder="Tunis"
            />
          </VCol>
          <VCol cols="12" md="4">
            <AppSelect
              v-model="filters.category"
              label="Catégorie"
              :items="[
                { title: 'Toutes les catégories', value: '' },
                ...categories.map(category => ({ title: category.name, value: String(category.id) })),
              ]"
            />
          </VCol>
        </VRow>

        <div class="d-flex flex-wrap gap-3 mt-2">
          <VBtn
            color="primary"
            rounded="pill"
            @click="fetchEvents"
          >
            Appliquer
          </VBtn>
          <VBtn
            variant="text"
            rounded="pill"
            @click="clearFilters"
          >
            Réinitialiser
          </VBtn>
        </div>
      </VCardText>
    </VCard>

    <VAlert
      v-if="errorMessage"
      type="error"
      variant="tonal"
    >
      {{ errorMessage }}
    </VAlert>

    <VAlert
      v-if="successMessage"
      type="success"
      variant="tonal"
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
        <VSkeletonLoader type="article@4" />
      </VCol>

      <VCol
        v-for="event in events"
        v-else
        :key="event.id"
        cols="12"
        md="6"
        xl="4"
      >
        <EventCard :event="event" />
      </VCol>
    </VRow>

    <VCard
      v-if="!isLoading && !events.length"
      class="section-card"
    >
      <VCardText class="pa-10 text-center">
        <VIcon
          icon="tabler-ticket-off"
          size="42"
          class="mb-3"
        />
        <h3 class="text-h5 mb-2">
          Aucun événement disponible
        </h3>
        <p class="text-medium-emphasis mb-0">
          Essayez un autre filtre ou revenez après validation de nouveaux événements.
        </p>
      </VCardText>
    </VCard>
  </div>
</template>

<style scoped>
.events-hero {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 1rem;
}
</style>
