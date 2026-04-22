<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import AppSelect from '@/@core/components/app-form-elements/AppSelect.vue'
import AppTextField from '@/@core/components/app-form-elements/AppTextField.vue'
import EventCard from '@/components/events/EventCard.vue'
import EventForm from '@/components/events/EventForm.vue'
import { useCatalogStore } from '@/stores/catalog'
import { useAuthStore } from '@/stores/auth'

definePage({
  meta: {
    public: true,
    layout: 'default',
  },
})

const catalogStore = useCatalogStore()
const authStore = useAuthStore()
const { events, categories, loading, totalItems, page, pageSize, filters, snackbar } = storeToRefs(catalogStore)

const searchInput = ref(filters.value.search)
const showMobileFilters = ref(false)

const canCreateEvent = computed(() => authStore.role === 'organizer')
const eventForm = ref<typeof EventForm | null>(null)

const handleEventCreated = () => {
  catalogStore.fetchEvents({})
}

const cityInput = ref(filters.value.city)
const eventTypeInput = ref(filters.value.event_type)
const isFreeInput = ref(filters.value.is_free)
const orderingInput = ref(filters.value.ordering)
const categoryInput = ref<number | null>(filters.value.category)

const eventTypeOptions = [
  { title: 'Tous les types', value: '' },
  { title: 'En personne', value: 'in_person' },
  { title: 'En ligne', value: 'online' },
  { title: 'Hybride', value: 'hybrid' },
]

const priceOptions = [
  { title: 'Tous les prix', value: null },
  { title: 'Gratuit', value: true },
  { title: 'Payant', value: false },
]

const orderingOptions = [
  { title: 'Date - Recent', value: '-start_date' },
  { title: 'Date - Ancien', value: 'start_date' },
  { title: 'Plus populaire', value: '-average_rating' },
]

let debounceId: ReturnType<typeof setTimeout> | null = null

const fetchEvents = (targetPage = page.value, targetPageSize = pageSize.value) => {
  catalogStore.fetchEvents({ page: targetPage, pageSize: targetPageSize })
}

const applyFilters = () => {
  catalogStore.fetchEvents({
    page: 1,
    search: searchInput.value,
    city: cityInput.value,
    event_type: eventTypeInput.value,
    is_free: isFreeInput.value,
    ordering: orderingInput.value,
    category: categoryInput.value,
  })
}

const onTableOptionsUpdate = (options: { page: number; itemsPerPage: number }) => {
  if (options.page !== page.value || options.itemsPerPage !== pageSize.value)
    fetchEvents(options.page, options.itemsPerPage)
}

const resetFilters = () => {
  searchInput.value = ''
  cityInput.value = ''
  eventTypeInput.value = ''
  isFreeInput.value = null
  orderingInput.value = '-start_date'
  categoryInput.value = null
  catalogStore.resetFilters()
}

watch(searchInput, value => {
  if (debounceId)
    clearTimeout(debounceId)

  debounceId = setTimeout(() => {
    catalogStore.fetchEvents({ page: 1, search: value })
  }, 300)
})

watch([categoryInput, eventTypeInput, cityInput, isFreeInput, orderingInput], () => {
  applyFilters()
})

onMounted(async () => {
  await Promise.all([
    catalogStore.fetchCategories(),
    catalogStore.fetchEvents(),
  ])
})

onUnmounted(() => {
  if (debounceId)
    clearTimeout(debounceId)
})
</script>

<template>
  <div class="page-shell">
    <section class="page-hero events-hero">
      <div>
        <p class="page-kicker">
          Reservations modernes
        </p>
        <h1 class="text-h2 mb-2">
          Explorez des experiences validees et pretes a reserver
        </h1>
        <p class="text-medium-emphasis mb-0">
          Une galerie d'evenements approuves, presentee avec une navigation claire, une recherche rapide et un parcours d'achat simple.
        </p>
      </div>

      <div class="d-flex flex-wrap gap-3">
        <VBtn
          v-if="canCreateEvent"
          color="primary"
          prepend-icon="tabler-plus"
          rounded="pill"
          @click="eventForm?.open()"
        >
          Ajouter un evenement
        </VBtn>
        <VBtn
          variant="tonal"
          prepend-icon="tabler-filter"
          rounded="pill"
          class="d-md-none"
          @click="showMobileFilters = !showMobileFilters"
        >
          Filtres
        </VBtn>
      </div>
    </section>

    <VRow>
      <VCol cols="12" md="3" class="d-none d-md-block">
        <VCard class="sticky-filters">
          <VCardText>
            <h3 class="text-h6 mb-4">Filtres</h3>

            <AppTextField
              v-model="searchInput"
              label="Recherche"
              prepend-inner-icon="tabler-search"
              placeholder="Titre, ville..."
              class="mb-4"
            />

            <AppSelect
              v-model="categoryInput"
              label="Categorie"
              :items="[
                { title: 'Toutes', value: null },
                ...categories.map(c => ({ title: c.name, value: c.id })),
              ]"
              class="mb-4"
            />

            <AppSelect
              v-model="eventTypeInput"
              label="Type"
              :items="eventTypeOptions"
              class="mb-4"
            />

            <AppTextField
              v-model="cityInput"
              label="Ville"
              prepend-inner-icon="tabler-map-pin"
              placeholder="Tunis, Sfax..."
              class="mb-4"
            />

            <AppSelect
              v-model="isFreeInput"
              label="Prix"
              :items="priceOptions"
              class="mb-4"
            />

            <AppSelect
              v-model="orderingInput"
              label="Trier par"
              :items="orderingOptions"
              class="mb-4"
            />

            <VBtn
              block
              variant="tonal"
              color="secondary"
              @click="resetFilters"
            >
              Reinitialiser
            </VBtn>
          </VCardText>
        </VCard>
      </VCol>

      <VCol cols="12" md="9">
        <VCard v-if="showMobileFilters" class="d-md-none mb-4">
          <VCardText>
            <h3 class="text-h6 mb-4">Filtres</h3>

            <AppTextField
              v-model="searchInput"
              label="Recherche"
              prepend-inner-icon="tabler-search"
              class="mb-4"
            />

            <AppSelect
              v-model="categoryInput"
              label="Categorie"
              :items="[
                { title: 'Toutes', value: null },
                ...categories.map(c => ({ title: c.name, value: c.id })),
              ]"
              class="mb-4"
            />

            <AppSelect
              v-model="eventTypeInput"
              label="Type"
              :items="eventTypeOptions"
              class="mb-4"
            />

            <AppSelect
              v-model="isFreeInput"
              label="Prix"
              :items="priceOptions"
              class="mb-4"
            />

            <VBtn
              block
              variant="tonal"
              color="secondary"
              @click="resetFilters"
            >
              Reinitialiser
            </VBtn>
          </VCardText>
        </VCard>

        <VRow>
          <VCol
            v-for="event in events"
            :key="event.id"
            cols="12"
            sm="6"
            lg="4"
          >
            <EventCard :event="event" />
          </VCol>
        </VRow>

        <div v-if="!loading && events.length === 0" class="text-center py-12">
          <VIcon icon="tabler-ticket-off" size="48" class="mb-4" />
          <h3 class="text-h5 mb-2">
            Aucun evenement disponible
          </h3>
          <p class="text-medium-emphasis mb-4">
            Essayez un autre filtre ou revenez plus tard.
          </p>
          <VBtn color="primary" @click="resetFilters">
            Reinitialiser les filtres
          </VBtn>
        </div>

        <div v-if="totalItems > pageSize" class="d-flex justify-center mt-6">
          <VPagination
            :model-value="page"
            :length="Math.ceil(totalItems / pageSize)"
            :total-visible="7"
            @update:model-value="fetchEvents"
          />
        </div>
      </VCol>
    </VRow>

    <VSnackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      timeout="3500"
    >
      {{ snackbar.message }}
    </VSnackbar>

    <EventForm ref="eventForm" @submit="handleEventCreated" />
  </div>
</template>

<style scoped>
.events-hero {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 1rem;
}

.sticky-filters {
  position: sticky;
  top: 1rem;
}
</style>