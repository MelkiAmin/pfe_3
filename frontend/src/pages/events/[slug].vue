<script setup lang="ts">
import AppSelect from '@/@core/components/app-form-elements/AppSelect.vue'
import AppTextField from '@/@core/components/app-form-elements/AppTextField.vue'
import LazyImage from '@/components/common/LazyImage.vue'
import { eventsApi, ticketsApi } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import type { EventDetail, TicketType } from '@/services/api'

definePage({
  meta: {
    public: true,
    layout: 'default',
  },
})

const route = useRoute()
const authStore = useAuthStore()
const cartStore = useCartStore()

const eventData = ref<EventDetail | null>(null)
const ticketTypes = ref<TicketType[]>([])
const selectedTicketTypeId = ref<number | null>(null)
const quantity = ref(1)
const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')

const selectedTicket = computed(() => ticketTypes.value.find(ticket => ticket.id === selectedTicketTypeId.value))
const availableTickets = computed(() => selectedTicket.value?.available_quantity || 0)
const currentPrice = computed(() => Number(selectedTicket.value?.price || 0))
const estimatedTotal = computed(() => currentPrice.value * quantity.value)
const canAddToBasket = computed(() =>
  authStore.role === 'attendee'
  && Boolean(selectedTicket.value)
  && availableTickets.value >= quantity.value
  && quantity.value > 0)

const loadPage = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const slug = String(route.params.slug || '').trim()
    const events = await eventsApi.list({ status: 'approved' })
    const found = events.find(event => event.slug === slug || `id-${event.id}` === slug)

    if (!found) {
      errorMessage.value = 'Event not found.'
      return
    }

    eventData.value = await eventsApi.getById(found.id)
    ticketTypes.value = await ticketsApi.listTicketTypes({ event: found.id })
    selectedTicketTypeId.value = ticketTypes.value[0]?.id || null
  }
  catch {
    errorMessage.value = 'Unable to load event details.'
  }
  finally {
    loading.value = false
  }
}

const addToCart = () => {
  if (!eventData.value || !selectedTicket.value || !canAddToBasket.value)
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

  successMessage.value = `${quantity.value} billet(s) ajouté(s) au panier.`
}

watch(selectedTicketTypeId, () => {
  quantity.value = 1
  successMessage.value = ''
})

onMounted(loadPage)
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

  <div
    v-else-if="eventData"
    class="page-shell"
  >
    <section class="page-hero event-hero">
      <div class="event-hero__cover">
        <LazyImage
          :src="eventData.cover_image"
          :height="420"
          alt="cover"
        />
      </div>

      <div class="event-hero__copy">
        <VChip
          color="success"
          variant="flat"
          class="mb-4"
        >
          Approved
        </VChip>
        <h1 class="text-h2 mb-3">
          {{ eventData.title }}
        </h1>
        <p class="text-body-1 text-medium-emphasis mb-4">
          {{ eventData.description }}
        </p>

        <div class="soft-grid soft-grid--3">
          <div class="info-tile">
            <span class="text-medium-emphasis">Organisateur</span>
            <strong>{{ eventData.organizer.full_name }}</strong>
          </div>
          <div class="info-tile">
            <span class="text-medium-emphasis">Lieu</span>
            <strong>{{ eventData.city || eventData.venue_name || 'Online' }}</strong>
          </div>
          <div class="info-tile">
            <span class="text-medium-emphasis">Tickets disponibles</span>
            <strong>{{ availableTickets }}</strong>
          </div>
        </div>
      </div>
    </section>

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
      <VCol cols="12" lg="8">
        <VCard class="section-card">
          <VCardText class="pa-6 pa-md-8">
            <p class="page-kicker">
              Event overview
            </p>
            <h3 class="text-h4 mb-3">
              What to expect
            </h3>
            <p class="text-medium-emphasis mb-0">
              {{ eventData.description }}
            </p>
          </VCardText>
        </VCard>
      </VCol>

      <VCol cols="12" lg="4">
        <VCard class="section-card booking-card">
          <VCardText class="pa-6">
            <p class="page-kicker">
              Reserve now
            </p>
            <h3 class="text-h4 mb-2">
              {{ currentPrice.toFixed(2) }} EUR
            </h3>
            <p class="text-medium-emphasis mb-5">
              Select your ticket type, choose quantity and add it to the basket.
            </p>

            <AppSelect
              v-model="selectedTicketTypeId"
              label="Ticket type"
              :items="ticketTypes.map(ticket => ({ title: `${ticket.name} · ${ticket.price} EUR`, value: ticket.id }))"
            />

            <AppTextField
              v-model.number="quantity"
              class="mt-4"
              type="number"
              min="1"
              :max="availableTickets || 1"
              label="Quantity"
            />

            <div class="booking-summary mt-4">
              <div class="d-flex justify-space-between mb-2">
                <span>Available tickets</span>
                <strong>{{ availableTickets }}</strong>
              </div>
              <div class="d-flex justify-space-between mb-2">
                <span>Total</span>
                <strong>{{ estimatedTotal.toFixed(2) }} EUR</strong>
              </div>
              <div class="text-medium-emphasis text-body-2">
                {{ canAddToBasket ? 'Ready to add to basket' : 'Connect as utilisateur to reserve tickets' }}
              </div>
            </div>

            <VBtn
              class="mt-4"
              block
              size="large"
              color="primary"
              :disabled="!canAddToBasket"
              @click="addToCart"
            >
              Add to Basket
            </VBtn>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
  </div>
</template>

<style scoped>
.event-hero {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 1.5rem;
}

.event-hero__cover {
  overflow: hidden;
  border-radius: 26px;
}

.event-hero__copy {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.info-tile {
  padding: 1rem;
  border-radius: 22px;
  background: rgba(var(--v-theme-primary), 0.06);
}

.booking-summary {
  padding: 1rem;
  border-radius: 22px;
  background: rgba(var(--v-theme-primary), 0.05);
}

@media (max-width: 1280px) {
  .event-hero {
    grid-template-columns: 1fr;
  }
}
</style>
