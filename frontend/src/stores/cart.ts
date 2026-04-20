import { defineStore } from 'pinia'
import { paymentsApi } from '@/services/api'

export type CartItem = {
  key: string
  eventId: number
  eventTitle: string
  ticketTypeId: number
  ticketTypeName: string
  unitPrice: number
  quantity: number
  availableQuantity: number
}

type CheckoutResult = {
  payment_id: number
  checkout_url: string
  session_id: string
}

const STORAGE_KEY = 'hotelmate_cart'

const parseCart = (): CartItem[] => {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  }
  catch {
    return []
  }
}

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: parseCart() as CartItem[],
    checkoutLoading: false,
  }),
  getters: {
    subtotal: state => state.items.reduce((sum, item) => sum + item.unitPrice * item.quantity, 0),
    fees(): number {
      return Number((this.subtotal * 0.03).toFixed(2))
    },
    total(): number {
      return Number((this.subtotal + this.fees).toFixed(2))
    },
    totalQuantity: state => state.items.reduce((sum, item) => sum + item.quantity, 0),
  },
  actions: {
    persist() {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(this.items))
    },

    addItem(item: Omit<CartItem, 'key'>) {
      const key = `${item.eventId}-${item.ticketTypeId}`
      const existing = this.items.find(i => i.key === key)

      if (existing) {
        const nextQty = existing.quantity + item.quantity
        existing.quantity = Math.min(nextQty, existing.availableQuantity)
      }
      else {
        this.items.push({
          ...item,
          key,
          quantity: Math.min(item.quantity, item.availableQuantity),
        })
      }

      this.persist()
    },

    removeItem(key: string) {
      this.items = this.items.filter(item => item.key !== key)
      this.persist()
    },

    updateQuantity(key: string, quantity: number) {
      const item = this.items.find(i => i.key === key)
      if (!item)
        return

      if (quantity <= 0) {
        this.removeItem(key)
        return
      }

      item.quantity = Math.min(quantity, item.availableQuantity)
      this.persist()
    },

    clear() {
      this.items = []
      this.persist()
    },

    validateStocks() {
      return this.items.every(item => item.quantity <= item.availableQuantity)
    },

    async checkout(): Promise<CheckoutResult> {
      if (!this.validateStocks())
        throw new Error('Stock insuffisant pour un ou plusieurs billets.')
      if (this.items.length !== 1)
        throw new Error('Le checkout supporte actuellement un seul type de billet à la fois.')

      this.checkoutLoading = true
      try {
        const [item] = this.items
        return await paymentsApi.createCheckoutSession({
          ticket_type_id: item.ticketTypeId,
          quantity: item.quantity,
          success_url: `${window.location.origin}/history`,
          cancel_url: `${window.location.origin}/events/id-${item.eventId}`,
        })
      }
      finally {
        this.checkoutLoading = false
      }
    },
  },
})
