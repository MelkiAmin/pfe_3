<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()
const drawer = ref(false)
const checkoutError = ref('')

const goCheckout = async () => {
  checkoutError.value = ''
  if (!authStore.isAuthenticated) {
    await router.push(`/login?redirect=${encodeURIComponent('/events')}`)
    return
  }

  try {
    const checkout = await cartStore.checkout()
    window.location.href = checkout.checkout_url
  }
  catch (error: any) {
    checkoutError.value = error?.message || 'Impossible de lancer le paiement.'
  }
}
</script>

<template>
  <div>
    <VBtn
      class="floating-cart-btn"
      color="primary"
      icon
      size="x-large"
      @click="drawer = true"
    >
      <VBadge
        :content="cartStore.totalQuantity"
        :model-value="cartStore.totalQuantity > 0"
        color="error"
      >
        <VIcon icon="tabler-shopping-bag" />
      </VBadge>
    </VBtn>

    <VNavigationDrawer
      v-model="drawer"
      location="end"
      temporary
      width="400"
    >
      <VToolbar
        density="comfortable"
        title="Votre panier"
      >
        <template #append>
          <IconBtn @click="drawer = false">
            <VIcon icon="tabler-x" />
          </IconBtn>
        </template>
      </VToolbar>

      <VDivider />

      <div class="cart-panel">
        <VAlert
          v-if="checkoutError"
          type="error"
          variant="tonal"
        >
          {{ checkoutError }}
        </VAlert>

        <VList
          lines="three"
          class="cart-list"
        >
          <VListItem
            v-for="item in cartStore.items"
            :key="item.key"
            :title="item.eventTitle"
            :subtitle="`${item.quantity} billet(s) · ${item.ticketTypeName}`"
            class="cart-item"
          >
            <template #append>
              <div class="text-end">
                <div class="font-weight-bold">
                  {{ (item.unitPrice * item.quantity).toFixed(2) }} DT
                </div>
                <IconBtn @click="cartStore.removeItem(item.key)">
                  <VIcon icon="tabler-trash" />
                </IconBtn>
              </div>
            </template>
          </VListItem>
        </VList>

        <VSheet
          class="cart-summary"
          rounded="xl"
        >
          <div class="d-flex justify-space-between mb-2">
            <span>Événements</span>
            <strong>{{ cartStore.totalQuantity }}</strong>
          </div>
          <div class="d-flex justify-space-between mb-2">
            <span>Sous-total</span>
            <strong>{{ cartStore.subtotal.toFixed(2) }} DT</strong>
          </div>
          <div class="d-flex justify-space-between mb-2">
            <span>Frais</span>
            <strong>{{ cartStore.fees.toFixed(2) }} DT</strong>
          </div>
          <div class="d-flex justify-space-between text-h6">
            <span>Total</span>
            <strong>{{ cartStore.total.toFixed(2) }} DT</strong>
          </div>
        </VSheet>

        <VBtn
          block
          size="large"
          color="primary"
          :disabled="!cartStore.items.length"
          :loading="cartStore.checkoutLoading"
          @click="goCheckout"
        >
          Passer au paiement
        </VBtn>
      </div>
    </VNavigationDrawer>
  </div>
</template>

<style scoped>
.floating-cart-btn {
  position: fixed;
  right: 22px;
  bottom: 24px;
  z-index: 1000;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.18);
}

.cart-panel {
  display: grid;
  gap: 1rem;
  padding: 1rem;
}

.cart-list {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 20px;
}

.cart-item {
  margin: 0.35rem;
  border-radius: 16px;
  background: rgba(var(--v-theme-primary), 0.04);
}

.cart-summary {
  padding: 1rem;
  background: rgba(var(--v-theme-primary), 0.06);
}
</style>
