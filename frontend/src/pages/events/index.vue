<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppSelect from '@/@core/components/app-form-elements/AppSelect.vue'
import EventCard from '@/components/events/EventCard.vue'
import { eventsApi } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

definePage({
  meta: {
    public: true,
  },
})

const router = useRouter()
const authStore = useAuthStore()

const events = ref<any[]>([])
const loading = ref(false)
const error = ref('')

const isOrganizer = computed(() => authStore.role === 'organizer')
const isUser = computed(() => authStore.role === 'attendee')

const showFilters = computed(() => isUser.value)

const selectedCategory = ref('')
const selectedDate = ref('')
const sortBy = ref('')

const categories = [
  { title: 'Tous', value: '' },
  { title: 'Musique', value: 'musique' },
  { title: 'Sport', value: 'sport' },
  { title: 'Tech', value: 'tech' },
  { title: 'Art', value: 'art' },
]

const dateOptions = [
  { title: 'Tous', value: '' },
  { title: 'Aujourd\'hui', value: 'today' },
  { title: 'Cette semaine', value: 'week' },
  { title: 'Ce mois', value: 'month' },
]

const sortOptions = [
  { title: 'Plus récent', value: '-created_at' },
  { title: 'Bientôt', value: 'start_date' },
  { title: 'Popularité', value: '-average_rating' },
]

onMounted(async () => {
  loading.value = true
  try {
    const response = await eventsApi.list({ page: 1, page_size: 12 })
    events.value = response?.results ?? []
  }
  catch (e: any) {
    error.value = e?.message || 'Erreur de connexion au serveur'
    console.error('Events error:', e)
  }
  finally {
    loading.value = false
  }
})

const goToCreate = () => {
  router.push('/events/create')
}
</script>

<template>
  <div class="pa-6">
    <div class="d-flex justify-space-between align-center mb-4">
      <div>
        <h1 class="text-h4 font-weight-bold mb-2">Événements</h1>
        <p class="text-medium-emphasis">Découvrez tous les événements disponibles</p>
      </div>
      <VBtn
        v-if="isOrganizer"
        color="primary"
        prepend-icon="tabler-plus"
        @click="goToCreate"
      >
        Ajouter un événement
      </VBtn>
    </div>

    <VAlert v-if="showFilters" type="info" variant="tonal" class="mb-4">
      <div class="d-flex flex-wrap gap-4">
        <AppSelect
          v-model="selectedCategory"
          label="Catégorie"
          :items="categories"
          clearable
          class="flex-grow-0"
          style="min-width: 150px"
        />
        <AppSelect
          v-model="selectedDate"
          label="Date"
          :items="dateOptions"
          clearable
          class="flex-grow-0"
          style="min-width: 150px"
        />
        <AppSelect
          v-model="sortBy"
          label="Trier par"
          :items="sortOptions"
          clearable
          class="flex-grow-0"
          style="min-width: 150px"
        />
      </div>
    </VAlert>

    <VProgressCircular v-if="loading" indeterminate color="primary" size="48" class="d-flex ma-auto" />

    <!-- Erreur -->
    <VAlert v-else-if="error" type="error" variant="tonal" class="mb-4">
      {{ error }} — Vérifiez que le serveur Django tourne sur le port 8000.
    </VAlert>

    <!-- Liste -->
    <VRow v-else-if="events.length > 0">
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

    <!-- Vide -->
    <div v-else class="d-flex flex-column align-center justify-center text-center pa-8">
      <VIcon icon="tabler-calendar-off" size="64" color="secondary" class="mb-4" />
      <h3 class="text-h5 mb-2">Aucun événement disponible</h3>
      <p class="text-medium-emphasis">Revenez bientôt.</p>
    </div>
  </div>
</template>