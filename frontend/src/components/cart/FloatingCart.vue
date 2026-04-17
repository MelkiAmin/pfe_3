<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()
const drawer = ref(false)

const goCheckout = async () => {
  if (!authStore.isAuthenticated) {
    await router.push(`/login?redirect=${encodeURIComponent('/checkout/new')}`)
    return
  }

  try {
    const order = await cartStore.checkout()
    await router.push(`/checkout/${order.id}`)
  }
  catch (error) {
    console.error(error)
  }
}
</script>

<template>
  <div>
    <VBtn
      class="floating-cart-btn"
      color="primary"
      icon
      @click="drawer = true"
    >
      <VBadge
        :content="cartStore.totalQuantity"
        :model-value="cartStore.totalQuantity > 0"
        color="error"
      >
        <VIcon icon="tabler-shopping-cart" />
      </VBadge>
    </VBtn>

    <VNavigationDrawer
      v-model="drawer"
      location="end"
      temporary
      width="380"
    >
      <VToolbar
        density="comfortable"
        title="Panier"
      >
        <template #append>
          <IconBtn @click="drawer = false">
            <VIcon icon="tabler-x" />
          </IconBtn>
        </template>
      </VToolbar>

      <VDivider />

      <VList lines="two">
        <VListItem
          v-for="item in cartStore.items"
          :key="item.key"
          :title="item.eventTitle"
          :subtitle="`${item.ticketTypeName} • ${item.quantity} x ${item.unitPrice.toFixed(2)}€`"
        >
          <template #append>
            <IconBtn @click="cartStore.removeItem(item.key)">
              <VIcon icon="tabler-trash" />
            </IconBtn>
          </template>
        </VListItem>
      </VList>

      <div class="pa-4 mt-auto">
        <VSheet
          border
          rounded
          class="pa-3 mb-3"
        >
          <div class="d-flex justify-space-between text-body-2 mb-1">
            <span>Sous-total</span>
            <strong>{{ cartStore.subtotal.toFixed(2) }}€</strong>
          </div>
          <div class="d-flex justify-space-between text-body-2 mb-1">
            <span>Frais</span>
            <strong>{{ cartStore.fees.toFixed(2) }}€</strong>
          </div>
          <div class="d-flex justify-space-between text-body-1">
            <span>Total</span>
            <strong>{{ cartStore.total.toFixed(2) }}€</strong>
          </div>
        </VSheet>

        <VBtn
          block
          color="primary"
          :disabled="!cartStore.items.length"
          :loading="cartStore.checkoutLoading"
          @click="goCheckout"
        >
          Passer à la caisse
        </VBtn>
      </div>
    </VNavigationDrawer>
  </div>
</template>

<style scoped>
.floating-cart-btn {
  position: fixed;
  right: 16px;
  bottom: 90px;
  z-index: 1000;
}
</style>
