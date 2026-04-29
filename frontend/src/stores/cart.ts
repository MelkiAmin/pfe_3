import { defineStore } from 'pinia'
import { paymentsApi } from '@/services/api'
import { authSession } from '@/services/http/axios'

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

type GroupedCheckout = {
  eventId: number
  eventTitle: string
  items: CartItem[]
  total: number
  checkoutUrl?: string
}

const STORAGE_KEY = 'hotelmate_cart'

const parseCart = (): CartItem[] => {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
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
    eventsInCart: state => {
      const eventIds = Array.from(new Set(state.items.map(item => item.eventId)))
      return eventIds
    },
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

    getItemsForEvent(eventId: number) {
      return this.items.filter(item => item.eventId === eventId)
    },

    validateBeforeCheckout(): string | null {
      if (!this.items.length) return 'Votre panier est vide.'
      if (!this.validateStocks()) return 'Stock insuffisant pour un ou plusieurs billets.'
      
      for (const item of this.items) {
        if (!item.eventId || !item.ticketTypeId) return 'Données panier invalides.'
        if (!item.quantity || item.quantity < 1) return 'Quantité invalide.'
        if (item.quantity > item.availableQuantity) return `Plus assez de places pour ${item.eventTitle}.`
      }
      return null
    },

    getCheckoutPayload(item: CartItem) {
      return {
        ticket_type_id: item.ticketTypeId,
        quantity: item.quantity,
        success_url: `${window.location.origin}/history`,
        cancel_url: `${window.location.origin}/events/${item.eventId}`,
      }
    },

    async checkoutForEvent(eventId: number): Promise<CheckoutResult> {
      const { access } = authSession.getTokens()
      if (!access) throw new Error('Veuillez vous connecter pour effectuer un paiement.')

      const eventItems = this.getItemsForEvent(eventId)
      if (eventItems.length === 0) throw new Error('Aucun article pour cet evenement.')
      if (!eventItems.every(item => item.quantity <= item.availableQuantity)) throw new Error('Stock insuffisant.')

      this.checkoutLoading = true
      try {
        const item = eventItems[0]
        const result = await paymentsApi.createCheckoutSession(this.getCheckoutPayload(item))
        if (!result.checkout_url) throw new Error('Erreur Stripe: URL de paiement manquante.')
        return result
      } finally {
        this.checkoutLoading = false
      }
    },

    async checkout(): Promise<GroupedCheckout[]> {
      const { access } = authSession.getTokens()
      if (!access) throw new Error('Veuillez vous connecter pour effectuer un paiement.')

      const validationError = this.validateBeforeCheckout()
      if (validationError) throw new Error(validationError)

      if (this.items.length === 0) throw new Error('Votre panier est vide.')

      this.checkoutLoading = true
      try {
        const results: GroupedCheckout[] = []
        const uniqueEventIds = Array.from(new Set(this.items.map(i => i.eventId))) as number[]

        for (const eventId of uniqueEventIds) {
          const eventItems = this.getItemsForEvent(eventId)
          if (!eventItems.length) continue

          const item = eventItems[0]
          if (item.quantity > item.availableQuantity) {
            throw new Error(`Places insuffisantes pour ${item.eventTitle}`)
          }

          const result = await paymentsApi.createCheckoutSession(this.getCheckoutPayload(item))
          
          if (!result.checkout_url) {
            throw new Error(`Erreur Stripe pour ${item.eventTitle}`)
          }

          results.push({
            eventId,
            eventTitle: item.eventTitle,
            items: eventItems,
            total: eventItems.reduce((sum, i) => sum + i.unitPrice * i.quantity, 0),
            checkoutUrl: result.checkout_url,
          })
        }

        return results
      } catch (error: any) {
        console.error('[Cart] Checkout error:', error)
        throw error
      } finally {
        this.checkoutLoading = false
      }
    },
  },
})