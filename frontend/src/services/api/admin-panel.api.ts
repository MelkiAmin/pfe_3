import { $api } from '@/utils/api'
import { unwrapListResponse } from './list-response'
import type { AdminDashboardStats, AdminUser, AdminUserStatus, AuthUser, EventDetail, EventListItem, EventPayload, OrganizerProfile } from './types'
import type { ListResponse, PaginatedResponse } from './list-response'

export type AdminUserListParams = {
  page?: number
  page_size?: number
  search?: string
  role?: 'attendee' | 'organizer' | 'admin'
  is_active?: boolean
  status?: AdminUserStatus
}

export type AdminUserUpdatePayload = {
  email?: string
  first_name?: string
  last_name?: string
  phone?: string
  role?: 'attendee' | 'organizer' | 'admin'
  account_status?: AdminUserStatus
}

export type AdminOrganizerListParams = {
  page?: number
  page_size?: number
  search?: string
  is_verified?: boolean
}

export type AdminOrganizerUpdatePayload = {
  organization_name?: string
  bio?: string
  website?: string
  social_links?: Record<string, string>
  is_verified?: boolean
}

export type AdminOrganizerStats = {
  total_events: number
  published_events: number
  total_tickets_sold: number
  total_revenue: string | number
}

export const adminPanelApi = {
  getDashboard() {
    return $api<AdminDashboardStats>('/admin-panel/dashboard/')
  },

  listUsers(params?: AdminUserListParams) {
    return $api<PaginatedResponse<AdminUser>>('/admin-panel/users/', { query: params })
  },

  getUser(userId: number | string) {
    return $api<AdminUser>(`/admin-panel/users/${userId}/`)
  },

  updateUser(userId: number | string, payload: AdminUserUpdatePayload) {
    return $api<AdminUser>(`/admin-panel/users/${userId}/`, {
      method: 'PATCH',
      body: payload,
    })
  },

  removeUser(userId: number | string) {
    return $api<void>(`/admin-panel/users/${userId}/`, {
      method: 'DELETE',
    })
  },

  banUser(userId: number | string, reason: string) {
    return $api<AdminUser>(`/admin-panel/users/${userId}/ban/`, {
      method: 'POST',
      body: { reason },
    })
  },

  unbanUser(userId: number | string) {
    return $api<AdminUser>(`/admin-panel/users/${userId}/unban/`, {
      method: 'POST',
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

  listOrganizers(params?: AdminOrganizerListParams) {
    return $api<PaginatedResponse<OrganizerProfile>>('/admin-panel/organizers/', { query: params })
  },

  getOrganizer(organizerId: number | string) {
    return $api<OrganizerProfile>(`/admin-panel/organizers/${organizerId}/`)
  },

  updateOrganizer(organizerId: number | string, payload: AdminOrganizerUpdatePayload) {
    return $api<OrganizerProfile>(`/admin-panel/organizers/${organizerId}/`, {
      method: 'PATCH',
      body: payload,
    })
  },

  removeOrganizer(organizerId: number | string) {
    return $api<void>(`/admin-panel/organizers/${organizerId}/`, {
      method: 'DELETE',
    })
  },

  getOrganizerStats(organizerId: number | string) {
    return $api<AdminOrganizerStats>(`/admin-panel/organizers/${organizerId}/stats/`)
  },

  listOrganizerEvents(organizerId: number | string, params?: { status?: string }) {
    return $api<ListResponse<EventListItem>>(`/admin-panel/organizers/${organizerId}/events/`, { query: params }).then(unwrapListResponse)
  },
}
