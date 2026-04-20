import { $api } from '@/utils/api'
import { unwrapListResponse } from './list-response'
import type { AdminDashboardStats, AuthUser, EventDetail, EventListItem, EventPayload } from './types'
import type { ListResponse } from './list-response'

export type AdminUserListParams = {
  search?: string
  role?: 'attendee' | 'organizer' | 'admin'
  is_active?: boolean
}

export const adminPanelApi = {
  getDashboard() {
    return $api<AdminDashboardStats>('/admin-panel/dashboard/')
  },

  listUsers(params?: AdminUserListParams) {
    return $api<ListResponse<AuthUser>>('/admin-panel/users/', { query: params }).then(unwrapListResponse)
  },

  getUser(userId: number | string) {
    return $api<AuthUser>(`/admin-panel/users/${userId}/`)
  },

  updateUser(userId: number | string, payload: Partial<AuthUser>) {
    return $api<AuthUser>(`/admin-panel/users/${userId}/`, {
      method: 'PATCH',
      body: payload,
    })
  },

  removeUser(userId: number | string) {
    return $api<void>(`/admin-panel/users/${userId}/`, {
      method: 'DELETE',
    })
  },

  listEvents(params?: { status?: string }) {
    return $api<ListResponse<EventListItem>>('/admin-panel/events/', { query: params }).then(unwrapListResponse)
  },

  getEvent(eventId: number | string) {
    return $api<EventDetail>(`/admin-panel/events/${eventId}/`)
  },

  updateEvent(eventId: number | string, payload: Partial<EventPayload> | FormData) {
    return $api<EventDetail>(`/admin-panel/events/${eventId}/`, {
      method: 'PATCH',
      body: payload,
    })
  },

  removeEvent(eventId: number | string) {
    return $api<void>(`/admin-panel/events/${eventId}/`, {
      method: 'DELETE',
    })
  },

  moderateEvent(eventId: number | string, payload: { action: 'approve' | 'reject'; reason?: string }) {
    return $api<EventDetail>(`/admin-panel/events/${eventId}/moderate/`, {
      method: 'POST',
      body: payload,
    })
  },
}
