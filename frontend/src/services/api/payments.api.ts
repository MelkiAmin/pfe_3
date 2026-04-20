import { $api } from '@/utils/api'
import { unwrapListResponse } from './list-response'
import type { CheckoutSessionPayload, CheckoutSessionResponse, Payment } from './types'
import type { ListResponse } from './list-response'

export const paymentsApi = {
  listHistory() {
    return $api<ListResponse<Payment>>('/payments/history/').then(unwrapListResponse)
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
