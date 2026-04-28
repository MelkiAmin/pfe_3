<script setup lang="ts">
import { useRoute } from 'vue-router'
import AppSelect from '@/@core/components/app-form-elements/AppSelect.vue'
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
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const selectedTicket = computed(() => ticketTypes.value.find(ticket => ticket.id === selectedTicketTypeId.value))
const availableTickets = computed(() => selectedTicket.value?.available_quantity || 0)
const currentPrice = computed(() => Number(selectedTicket.value?.price || 0))
const estimatedTotal = computed(() => currentPrice.value * quantity.value)
const isFreeEvent = computed(() => !selectedTicket.value || currentPrice.value === 0)
const isValidQuantity = computed(() => quantity.value >= 1 && quantity.value <= availableTickets.value)
const maxQuantity = computed(() => Math.max(1, availableTickets.value))
const canAddToBasket = computed(() =>
  authStore.role === 'attendee'
  && Boolean(selectedTicket.value)
  && availableTickets.value >= quantity.value
  && quantity.value > 0)

const resetState = () => {
  eventData.value = null
  ticketTypes.value = []
  selectedTicketTypeId.value = null
  quantity.value = 1
  errorMessage.value = ''
  successMessage.value = ''
}

const loadPage = async (id: number) => {
  if (!id || isNaN(id)) {
    errorMessage.value = 'ID invalide.'
    return
  }

  resetState()
  loading.value = true

  try {
    const event = await eventsApi.getById(id)
    eventData.value = event

    ticketTypes.value = event?.ticket_types ||
      await ticketsApi.listTicketTypes({ event: event.id })

    selectedTicketTypeId.value = ticketTypes.value[0]?.id || null
  }
  catch (error) {
    errorMessage.value = 'Échec du chargement.'
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

watch(availableTickets, (newMax) => {
  if (quantity.value > newMax) {
    quantity.value = Math.max(1, newMax)
  }
})

watch(
  () => route.params.id,
  (newId, oldId) => {
    if (!newId || newId === oldId) return
    const numId = Number(newId)
    if (isNaN(numId)) {
      errorMessage.value = 'ID invalide: ' + newId
      return
    }
    loadPage(numId)
  }
)

onMounted(() => {
  const id = route.params.id
  if (id) {
    const numId = Number(id)
    if (isNaN(numId)) {
      errorMessage.value = 'ID invalide: ' + id
      return
    }
    loadPage(numId)
  }
  else {
    errorMessage.value = 'Événement non spécifié.'
  }
})
</script>

<template>
  <div class="page-shell">
    <VAlert v-if="errorMessage" type="error" variant="tonal" class="mb-4">
      {{ errorMessage }}
    </VAlert>

    <div v-if="loading" class="loading-container">
      <VSkeletonLoader type="image, article, list-item-two-line@3" />
    </div>

    <template v-else-if="eventData">
      <section class="page-hero event-hero">
        <div class="event-hero__cover">
          <LazyImage :src="eventData.cover_image" :height="420" alt="cover" />
        </div>

        <div class="event-hero__copy">
          <VChip color="success" variant="flat" class="mb-4">Approuvé</VChip>
          <h1 class="text-h2 mb-3">{{ eventData.title }}</h1>
          <p class="text-body-1 text-medium-emphasis mb-4">{{ eventData.description }}</p>

          <div class="soft-grid soft-grid--3">
            <div class="info-tile">
              <span class="text-medium-emphasis">Organisateur</span>
              <strong>{{ eventData.organizer?.full_name || 'N/A' }}</strong>
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

      <VAlert v-if="successMessage" type="success" variant="tonal" closable class="mb-4" @click:close="successMessage = ''">
        {{ successMessage }}
      </VAlert>

      <VRow>
        <VCol cols="12" lg="8">
          <VCard class="section-card">
            <VCardText class="pa-6 pa-md-8">
              <p class="page-kicker">Vue d'ensemble</p>
              <h3 class="text-h4 mb-3">Ce qui vous attend</h3>
              <p class="text-medium-emphasis mb-0">{{ eventData.description }}</p>
            </VCardText>
          </VCard>
        </VCol>

        <VCol cols="12" lg="4">
          <VCard class="section-card booking-card">
            <VCardText class="pa-6">
              <p class="page-kicker">Réserver maintenant</p>
              <h3 class="text-h4 mb-2">
                <span v-if="isFreeEvent">Gratuit</span>
                <span v-else>{{ currentPrice.toFixed(2) }} DT</span>
              </h3>
              <p class="text-medium-emphasis mb-5">Sélectionnez le type de billet et la quantité.</p>

              <AppSelect
                v-model="selectedTicketTypeId"
                label="Type de billet"
                :items="ticketTypes.map(ticket => ({ title: `${ticket.name} · ${ticket.price} DT`, value: ticket.id }))"
                :disabled="ticketTypes.length <= 1"
              />

              <div class="quantity-selector mt-4">
                <label class="text-body-2 text-wrap mb-1 d-block">Quantité</label>
                <div class="quantity-controls">
                  <VBtn icon size="small" variant="outlined" :disabled="quantity <= 1 || !isValidQuantity" @click="quantity = Math.max(1, quantity - 1)">
                    <VIcon icon="tabler-minus" size="18" />
                  </VBtn>
                  <span class="quantity-value">{{ quantity }}</span>
                  <VBtn icon size="small" variant="outlined" :disabled="quantity >= availableTickets || availableTickets <= 0" @click="quantity = Math.min(maxQuantity, quantity + 1)">
                    <VIcon icon="tabler-plus" size="18" />
                  </VBtn>
                </div>
                <p v-if="availableTickets > 0" class="text-caption text-medium-emphasis mt-1">
                  {{ availableTickets }} billet(s) disponible(s)
                </p>
                <p v-else class="text-caption text-error mt-1">Plus de billets disponibles</p>
              </div>

              <div class="booking-summary mt-4">
                <div class="d-flex justify-space-between mb-2">
                  <span>Prix unitaire</span>
                  <strong>{{ isFreeEvent ? 'Gratuit' : `${currentPrice.toFixed(2)} DT` }}</strong>
                </div>
                <div class="d-flex justify-space-between mb-2">
                  <span>Total</span>
                  <strong>{{ isFreeEvent ? 'Gratuit' : `${estimatedTotal.toFixed(2)} DT` }}</strong>
                </div>
                <div class="text-medium-emphasis text-body-2">
                  {{ authStore.role === 'attendee' ? 'Prêt à ajouter au panier' : 'Connectez-vous pour réserver' }}
                </div>
              </div>

              <VBtn class="mt-4" block size="large" color="primary" :disabled="!canAddToBasket" @click="addToCart">
                <VIcon icon="tabler-shopping-cart" class="mr-2" size="20" />
                Ajouter au panier
              </VBtn>
            </VCardText>
          </VCard>
        </VCol>
      </VRow>
    </template>
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

.quantity-selector {
  padding: 1rem;
  border-radius: 22px;
  background: rgba(var(--v-theme-primary), 0.05);
}

.quantity-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.quantity-value {
  font-size: 1.25rem;
  font-weight: 600;
  min-width: 2.5rem;
  text-align: center;
}

@media (max-width: 1280px) {
  .event-hero {
    grid-template-columns: 1fr;
  }
}
</style>