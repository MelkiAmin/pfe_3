<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import type { CartItem } from '@/stores/cart'

definePage({
  meta: {
    layout: 'default',
    requiresAuth: true,
  },
})

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()
const checkoutErrors = ref<Record<number, string>>({})
const processingEvents = ref<number[]>([])

const eventsGrouped = computed(() => {
  const eventIds = cartStore.eventsInCart
  return eventIds.map(eventId => {
    const items = cartStore.getItemsForEvent(eventId)
    const total = items.reduce((sum, item) => sum + item.unitPrice * item.quantity, 0)
    const quantity = items.reduce((sum, item) => sum + item.quantity, 0)
    return {
      eventId,
      eventTitle: items[0]?.eventTitle || `Event #${eventId}`,
      items,
      total,
      quantity,
    }
  })
})

const subtotal = computed(() => cartStore.subtotal)
const fees = computed(() => cartStore.fees)
const total = computed(() => cartStore.total)

const updateItemQuantity = (item: CartItem, delta: number) => {
  const newQty = item.quantity + delta
  if (newQty <= 0) {
    cartStore.removeItem(item.key)
  }
  else if (newQty <= item.availableQuantity) {
    cartStore.updateQuantity(item.key, newQty)
  }
}

const checkoutForEvent = async (eventId: number) => {
  checkoutErrors.value[eventId] = ''
  processingEvents.value.push(eventId)

  try {
    const result = await cartStore.checkoutForEvent(eventId)
    window.location.href = result.checkout_url
  }
  catch (error: any) {
    checkoutErrors.value[eventId] = error?.message || 'Impossible de lancer le paiement.'
  }
  finally {
    processingEvents.value = processingEvents.value.filter(id => id !== eventId)
  }
}

const goToEvent = (eventId: number) => {
  router.push(`/events/id-${eventId}`)
}
</script>

<template>
  <div class="cart-page">
    <div class="page-header mb-6">
      <h1 class="text-h4">Votre panier</h1>
      <p class="text-medium-emphasis">
        {{ cartStore.totalQuantity }} billet(s) dans votre panier
      </p>
    </div>

    <VAlert
      v-if="!cartStore.items.length"
      type="info"
      variant="tonal"
      class="mb-6"
    >
      Votre panier est vide.
      <template #append>
        <VBtn
          variant="text"
          size="small"
          @click="router.push('/events')"
        >
          Parcourir les événements
        </VBtn>
      </template>
    </VAlert>

    <VRow v-else>
      <VCol
        cols="12"
        lg="8"
      >
        <VCard
          v-for="eventGroup in eventsGrouped"
          :key="eventGroup.eventId"
          class="event-group-card mb-4"
        >
          <VCardText class="pa-0">
            <div class="event-header pa-4">
              <div class="d-flex justify-space-between align-center">
                <div>
                  <h3 class="text-h6 mb-1">
                    {{ eventGroup.eventTitle }}
                  </h3>
                  <VBtn
                    variant="text"
                    size="small"
                    @click="goToEvent(eventGroup.eventId)"
                  >
                    <VIcon icon="tabler-arrow-left" class="mr-1" size="16" />
                    Voir l'événement
                  </VBtn>
                </div>
                <div class="text-end">
                  <div class="text-h6">
                    {{ eventGroup.total.toFixed(2) }} DT
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ eventGroup.quantity }} billet(s)
                  </div>
                </div>
              </div>
            </div>

            <VDivider />

            <div class="items-list">
              <div
                v-for="item in eventGroup.items"
                :key="item.key"
                class="cart-item pa-4"
              >
                <div class="d-flex justify-space-between align-center">
                  <div class="item-info">
                    <div class="text-body-1 font-weight-medium">
                      {{ item.ticketTypeName }}
                    </div>
                    <div class="text-caption text-medium-emphasis">
                      {{ item.unitPrice.toFixed(2) }} DT / billet
                    </div>
                  </div>
                  <div class="item-controls d-flex align-center">
                    <VBtn
                      icon
                      size="small"
                      variant="outlined"
                      :disabled="item.quantity <= 1"
                      @click="updateItemQuantity(item, -1)"
                    >
                      <VIcon icon="tabler-minus" size="18" />
                    </VBtn>
                    <span class="quantity-display mx-3">
                      {{ item.quantity }}
                    </span>
                    <VBtn
                      icon
                      size="small"
                      variant="outlined"
                      :disabled="item.quantity >= item.availableQuantity"
                      @click="updateItemQuantity(item, 1)"
                    >
                      <VIcon icon="tabler-plus" size="18" />
                    </VBtn>
                    <VBtn
                      icon
                      size="small"
                      variant="text"
                      color="error"
                      class="ml-2"
                      @click="cartStore.removeItem(item.key)"
                    >
                      <VIcon icon="tabler-trash" size="18" />
                    </VBtn>
                  </div>
                </div>
                <div class="item-total text-end mt-2">
                  <strong>{{ (item.unitPrice * item.quantity).toFixed(2) }} DT</strong>
                </div>
              </div>
            </div>

            <VDivider />

            <div class="event-checkout pa-4">
              <VAlert
                v-if="checkoutErrors[eventGroup.eventId]"
                type="error"
                variant="tonal"
                class="mb-3"
              >
                {{ checkoutErrors[eventGroup.eventId] }}
              </VAlert>
              <VBtn
                block
                color="primary"
                size="large"
                :loading="processingEvents.includes(eventGroup.eventId)"
                @click="checkoutForEvent(eventGroup.eventId)"
              >
                <VIcon icon="tabler-credit-card" class="mr-2" />
                Payer pour cet événement
              </VBtn>
            </div>
          </VCardText>
        </VCard>
      </VCol>

      <VCol
        cols="12"
        lg="4"
      >
        <VCard class="sticky-summary">
          <VCardText>
            <h4 class="text-h6 mb-4">
              Récapitulatif
            </h4>
            <div class="summary-row d-flex justify-space-between mb-2">
              <span>Sous-total</span>
              <strong>{{ subtotal.toFixed(2) }} DT</strong>
            </div>
            <div class="summary-row d-flex justify-space-between mb-2">
              <span>Frais (3%)</span>
              <strong>{{ fees.toFixed(2) }} DT</strong>
            </div>
            <VDivider class="my-3" />
            <div class="summary-row d-flex justify-space-between text-h6">
              <span>Total</span>
              <strong>{{ total.toFixed(2) }} DT</strong>
            </div>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
  </div>
</template>

<style scoped>
.cart-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
}

.event-group-card {
  overflow: hidden;
}

.event-header {
  background: rgba(var(--v-theme-primary), 0.04);
}

.items-list {
  background: rgb(var(--v-theme-surface));
}

.cart-item {
  border-bottom: 1px solid rgba(var(--v-border-color), 0.08);
}

.cart-item:last-child {
  border-bottom: none;
}

.quantity-display {
  font-size: 1.125rem;
  font-weight: 600;
  min-width: 2rem;
  text-align: center;
}

.item-controls {
  gap: 0.25rem;
}

.sticky-summary {
  position: sticky;
  top: 1rem;
}

.summary-row {
  padding: 0.25rem 0;
}
</style>