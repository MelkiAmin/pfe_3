import { $api } from '@/utils/api'
import type { CheckoutSessionPayload, CheckoutSessionResponse, Payment } from './types'

export const paymentsApi = {
  listHistory() {
    return $api<Payment[]>('/payments/history/')
  },

  getPayment(paymentId: number | string) {
    return $api<Payment>(`/payments/history/${paymentId}/`)
  },

  createCheckoutSession(payload: CheckoutSessionPayload) {
    return $api<CheckoutSessionResponse>('/payments/checkout/', {
      method: 'POST',
      body: payload,
    })
  },

  sendStripeWebhook(payload: unknown) {
    return $api<{ status: string }>('/payments/webhook/stripe/', {
      method: 'POST',
      body: payload,
    })
  },
}
