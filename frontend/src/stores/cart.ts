import { defineStore } from 'pinia'
import { apiClient } from '@/services/http/axios'

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
  id: number
  status: string
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

      this.checkoutLoading = true
      try {
        const { data } = await apiClient.post('/orders', {
          items: this.items.map(item => ({
            event_id: item.eventId,
            ticket_type_id: item.ticketTypeId,
            quantity: item.quantity,
          })),
        })
        return data as CheckoutResult
      }
      finally {
        this.checkoutLoading = false
      }
    },
  },
})
