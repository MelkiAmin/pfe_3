import { $api } from '@/utils/api'
import type { AdminDashboardStats, AuthUser, EventDetail, EventListItem, EventPayload } from './types'

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
    return $api<AuthUser[]>('/admin-panel/users/', { query: params })
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

  listEvents() {
    return $api<EventListItem[]>('/admin-panel/events/')
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
}
