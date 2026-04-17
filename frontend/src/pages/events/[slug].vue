<script setup lang="ts">
import RatingStars from '@/components/common/RatingStars.vue'
import LazyImage from '@/components/common/LazyImage.vue'
import { fakeEvents } from '@/data/fake-events'
import { eventsApi, ticketsApi } from '@/services/api'
import { useCartStore } from '@/stores/cart'
import type { EventDetail, TicketType } from '@/services/api'

definePage({
  meta: {
    public: true,
    layout: 'default',
  },
})

const route = useRoute()
const cartStore = useCartStore()

const eventData = ref<EventDetail | null>(null)
const ticketTypes = ref<TicketType[]>([])
const selectedTicketTypeId = ref<number | null>(null)
const quantity = ref(1)
const loading = ref(true)
const availability = ref('')
const errorMessage = ref('')

const speakers = ref([
  { name: 'Mehdi Sellami', role: 'Founder', topic: 'Event strategy at scale' },
  { name: 'Amina Ben Ali', role: 'Product Lead', topic: 'From booking to check-in' },
])

const timeSlots = ref([
  { time: '09:00', title: 'Opening keynote' },
  { time: '11:00', title: 'Technical workshop' },
  { time: '14:00', title: 'Networking session' },
])

const selectedTicket = computed(() =>
  ticketTypes.value.find(ticket => ticket.id === selectedTicketTypeId.value))

const refreshAvailability = async () => {
  if (!eventData.value)
    return
  const latest = await ticketsApi.listTicketTypes({ event: eventData.value.id })
  ticketTypes.value = latest
  const ticket = selectedTicket.value
  availability.value = ticket
    ? `${ticket.available_quantity} restant(s)`
    : ''
}

const loadPage = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const routeParam = String(route.params.slug || '')
    const slug = routeParam.trim()
    const idMatch = slug.match(/^id-(\d+)$/)
    const forcedId = idMatch ? Number(idMatch[1]) : null
    let found = null as null | { id: number, slug: string, title: string, description?: string, cover_image?: string | null, category?: any, event_type?: any, status?: any, venue_name?: string, address?: string, city?: string, country?: string, online_url?: string, start_date?: string, end_date?: string, max_capacity?: number | null, is_free?: boolean, tickets_sold?: number, is_sold_out?: boolean, average_rating?: number, reviews_count?: number }

    if (forcedId && forcedId < 9000) {
      eventData.value = await eventsApi.getById(forcedId)
      ticketTypes.value = await ticketsApi.listTicketTypes({ event: forcedId })
      selectedTicketTypeId.value = ticketTypes.value[0]?.id || null
      await refreshAvailability()
      return
    }

    try {
      const events = await eventsApi.list()
      found = events.find((event) => {
        if (forcedId)
          return event.id === forcedId

        return event.slug === slug
      }) || null
    }
    catch {
      found = null
    }

    if (!found)
      found = fakeEvents.find(event => event.slug === slug) || null

    if (!found) {
      errorMessage.value = 'Event not found.'
      return
    }

    if (found.id < 9000) {
      eventData.value = await eventsApi.getById(found.id)
      ticketTypes.value = await ticketsApi.listTicketTypes({ event: found.id })
      selectedTicketTypeId.value = ticketTypes.value[0]?.id || null
      await refreshAvailability()
      return
    }

    eventData.value = {
      id: found.id,
      organizer: {
        id: 0,
        email: 'demo@planova.local',
        first_name: 'Demo',
        last_name: 'Organizer',
        full_name: found.title,
        role: 'organizer',
        avatar: null,
        phone: '',
        is_email_verified: true,
        created_at: new Date().toISOString(),
      },
      category: found.category || null,
      title: found.title,
      slug: found.slug,
      description: found.description || 'Event details preview (fake data mode).',
      cover_image: found.cover_image || null,
      event_type: found.event_type || 'in_person',
      status: found.status || 'published',
      venue_name: found.venue_name || 'Main Venue',
      address: found.address || '',
      city: found.city || '',
      country: found.country || '',
      online_url: found.online_url || '',
      start_date: found.start_date || new Date().toISOString(),
      end_date: found.end_date || new Date().toISOString(),
      max_capacity: found.max_capacity || 500,
      is_free: Boolean(found.is_free),
      tags: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      tickets_sold: Number(found.tickets_sold || 0),
      is_sold_out: Boolean(found.is_sold_out),
      average_rating: Number(found.average_rating || 0),
      reviews_count: Number(found.reviews_count || 0),
    }

    ticketTypes.value = [
      {
        id: 1,
        event: found.id,
        name: found.is_free ? 'Free Pass' : 'Standard',
        description: 'Fake ticket for preview mode',
        price: found.is_free ? '0' : '49',
        quantity: 500,
        quantity_sold: Number(found.tickets_sold || 0),
        available_quantity: found.is_sold_out ? 0 : 100,
        is_available: !found.is_sold_out,
        sale_start: null,
        sale_end: null,
      },
    ]
    selectedTicketTypeId.value = ticketTypes.value[0]?.id || null
    availability.value = ticketTypes.value[0]?.available_quantity
      ? `${ticketTypes.value[0].available_quantity} restant(s)`
      : 'Complet'
  }
  catch {
    errorMessage.value = 'Unable to load event details.'
  }
  finally {
    loading.value = false
  }
}

const addToCart = () => {
  if (!eventData.value || !selectedTicket.value)
    return

  cartStore.addItem({
    eventId: eventData.value.id,
    eventTitle: eventData.value.title,
    ticketTypeId: selectedTicket.value.id,
    ticketTypeName: selectedTicket.value.name,
    unitPrice: Number(selectedTicket.value.price || 0),
    quantity: quantity.value,
    availableQuantity: selectedTicket.value.available_quantity,
  })
}

watch(selectedTicketTypeId, refreshAvailability)
onMounted(loadPage)

let pollInterval: number | undefined
onMounted(() => {
  pollInterval = window.setInterval(() => {
    refreshAvailability().catch(() => {})
  }, 15000)
})

onBeforeUnmount(() => {
  if (pollInterval)
    window.clearInterval(pollInterval)
})
</script>

<template>
  <VAlert
    v-if="errorMessage"
    type="error"
    variant="tonal"
    class="mb-4"
  >
    {{ errorMessage }}
  </VAlert>
  <div v-if="loading">
    <VSkeletonLoader type="image, article, list-item-two-line@3" />
  </div>
  <div v-else-if="eventData">
    <VRow>
      <VCol
        cols="12"
        md="8"
      >
        <LazyImage
          :src="eventData.cover_image"
          :height="320"
          alt="cover"
        />
        <VCard class="mt-6">
          <VCardItem :title="eventData.title" />
          <VCardText>
            <p class="mb-4">
              {{ eventData.description }}
            </p>
            <div class="d-flex align-center gap-4 mb-4">
              <RatingStars
                :model-value="eventData.average_rating"
                readonly
              />
              <span class="text-body-2">{{ eventData.reviews_count }} avis</span>
            </div>

            <h5 class="text-h5 mb-2">
              Speakers
            </h5>
            <VList lines="one">
              <VListItem
                v-for="speaker in speakers"
                :key="speaker.name"
                :title="speaker.name"
                :subtitle="`${speaker.role} • ${speaker.topic}`"
              />
            </VList>

            <h5 class="text-h5 mt-4 mb-2">
              Time slots
            </h5>
            <VTimeline density="compact">
              <VTimelineItem
                v-for="slot in timeSlots"
                :key="slot.time"
                size="small"
              >
                <div class="text-subtitle-2">
                  {{ slot.time }}
                </div>
                <div class="text-body-2">
                  {{ slot.title }}
                </div>
              </VTimelineItem>
            </VTimeline>
          </VCardText>
        </VCard>
      </VCol>

      <VCol
        cols="12"
        md="4"
      >
        <VCard>
          <VCardItem title="Réservation" />
          <VCardText>
            <AppSelect
              v-model="selectedTicketTypeId"
              label="Catégorie ticket"
              :items="ticketTypes.map(ticket => ({ title: `${ticket.name} (${ticket.price}€)`, value: ticket.id }))"
            />
            <AppTextField
              v-model.number="quantity"
              class="mt-3"
              type="number"
              min="1"
              :max="selectedTicket?.available_quantity || 1"
              label="Quantité"
            />

            <VAlert
              class="mt-3"
              type="info"
              variant="tonal"
            >
              Disponibilité: {{ availability || 'N/A' }}
            </VAlert>

            <VBtn
              class="mt-4"
              block
              color="primary"
              :disabled="!selectedTicket || selectedTicket.available_quantity < 1"
              @click="addToCart"
            >
              Ajouter au panier
            </VBtn>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
  </div>
</template>
