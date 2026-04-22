<script setup lang="ts">
import { apiClient } from '@/services/http/axios'
import { useCartStore } from '@/stores/cart'

const route = useRoute()
const cartStore = useCartStore()
const processing = ref(false)
const paymentDone = ref(false)

const orderId = computed(() => String(route.params.orderId))

const pay = async (provider: 'stripe' | 'paypal') => {
  processing.value = true
  try {
    await apiClient.post(`/orders/${orderId.value}/pay`, { provider })
    paymentDone.value = true
    cartStore.clear()
  }
  finally {
    processing.value = false
  }
}
</script>

<template>
  <VRow>
    <VCol
      cols="12"
      md="8"
    >
      <VCard title="Paiement">
        <VCardText>
          <p class="mb-4">
            Commande #{{ orderId }}
          </p>

          <VAlert
            v-if="paymentDone"
            type="success"
            variant="tonal"
            class="mb-4"
          >
            Paiement confirmé. Les webhooks finaliseront la commande.
          </VAlert>

          <VSheet
            border
            rounded
            class="pa-4 mb-4"
          >
            <h6 class="text-h6 mb-2">
              Stripe Elements
            </h6>
            <p class="text-body-2 text-medium-emphasis mb-0">
              Zone carte (placeholder). Brancher le composant Stripe Elements ici.
            </p>
          </VSheet>

          <div class="d-flex flex-wrap gap-3">
            <VBtn
              color="primary"
              :loading="processing"
              @click="pay('stripe')"
            >
              Payer par carte
            </VBtn>
            <VBtn
              color="info"
              variant="tonal"
              :loading="processing"
              @click="pay('paypal')"
            >
              Payer avec PayPal
            </VBtn>
          </div>
        </VCardText>
      </VCard>
    </VCol>

    <VCol
      cols="12"
      md="4"
    >
      <VCard title="Récapitulatif">
        <VCardText>
          <div class="d-flex justify-space-between mb-1">
            <span>Sous-total</span>
            <strong>{{ cartStore.subtotal.toFixed(2) }} DT</strong>
          </div>
          <div class="d-flex justify-space-between mb-1">
            <span>Frais</span>
            <strong>{{ cartStore.fees.toFixed(2) }} DT</strong>
          </div>
          <div class="d-flex justify-space-between">
            <span>Total</span>
            <strong>{{ cartStore.total.toFixed(2) }} DT</strong>
          </div>
        </VCardText>
      </VCard>
    </VCol>
  </VRow>
</template>
