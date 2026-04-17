import { $api } from '@/utils/api'
import type { Ticket, TicketStatus, TicketType } from './types'

export type TicketTypePayload = {
  event: number
  name: string
  description?: string
  price: number | string
  quantity: number
  sale_start?: string | null
  sale_end?: string | null
}

export type TicketListParams = {
  event?: number
  status?: TicketStatus
}

export type TicketPayload = {
  ticket_type: number
  event: number
  status?: TicketStatus
  price_paid: number | string
}

export const ticketsApi = {
  listTicketTypes(params?: { event?: number }) {
    return $api<TicketType[]>('/tickets/types/', { query: params })
  },

  getTicketType(ticketTypeId: number | string) {
    return $api<TicketType>(`/tickets/types/${ticketTypeId}/`)
  },

  createTicketType(payload: TicketTypePayload) {
    return $api<TicketType>('/tickets/types/', {
      method: 'POST',
      body: payload,
    })
  },

  updateTicketType(ticketTypeId: number | string, payload: Partial<TicketTypePayload>) {
    return $api<TicketType>(`/tickets/types/${ticketTypeId}/`, {
      method: 'PATCH',
      body: payload,
    })
  },

  removeTicketType(ticketTypeId: number | string) {
    return $api<void>(`/tickets/types/${ticketTypeId}/`, { method: 'DELETE' })
  },

  listTickets(params?: TicketListParams) {
    return $api<Ticket[]>('/tickets/', { query: params })
  },

  getTicket(ticketId: number | string) {
    return $api<Ticket>(`/tickets/${ticketId}/`)
  },

  createTicket(payload: TicketPayload) {
    return $api<Ticket>('/tickets/', {
      method: 'POST',
      body: payload,
    })
  },

  removeTicket(ticketId: number | string) {
    return $api<void>(`/tickets/${ticketId}/`, { method: 'DELETE' })
  },

  checkInTicket(ticketId: number | string) {
    return $api<{ detail: string; ticket: Ticket }>(`/tickets/${ticketId}/check_in/`, {
      method: 'POST',
    })
  },
}
