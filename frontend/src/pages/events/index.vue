<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { eventsApi } from '@/services/api'

definePage({
  meta: {
    public: true,
    layout: 'default',
  },
})

const router = useRouter()
const events = ref([])
const loading = ref(false)
const error = ref('')

const loadEvents = async () => {
  loading.value = true
  try {
    events.value = await eventsApi.list()
  } catch (e) {
    error.value = 'Erreur chargement événements'
  } finally {
    loading.value = false
  }
}

const goToEvent = (id: number) => {
  router.push(`/events/${id}`)
}

onMounted(loadEvents)
</script>

<template>
  <div>
    <h1 class="text-h4 mb-4">Événements</h1>

    <VAlert v-if="error" type="error">{{ error }}</VAlert>

    <VProgressCircular v-if="loading" indeterminate />

    <VRow v-else>
      <VCol
        v-for="event in events"
        :key="event.id"
        cols="12"
        md="4"
      >
        <VCard @click="goToEvent(event.id)" class="cursor-pointer">
          <VCardTitle>{{ event.title }}</VCardTitle>
          <VCardText>
            {{ event.description?.slice(0, 80) }}...
          </VCardText>

          <VCardActions>
            <VBtn variant="text">Consulter</VBtn>
          </VCardActions>
        </VCard>
      </VCol>
    </VRow>
  </div>
</template>