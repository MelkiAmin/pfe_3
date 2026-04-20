import { $api } from '@/utils/api'
import { unwrapListResponse } from './list-response'
import type { Notification, UnreadCountResponse } from './types'
import type { ListResponse } from './list-response'

export const notificationsApi = {
  list() {
    return $api<ListResponse<Notification>>('/notifications/').then(unwrapListResponse)
  },

  getById(notificationId: number | string) {
    return $api<Notification>(`/notifications/${notificationId}/`)
  },

  remove(notificationId: number | string) {
    return $api<void>(`/notifications/${notificationId}/`, {
      method: 'DELETE',
    })
  },

  markAllRead() {
    return $api<{ detail: string }>('/notifications/mark_all_read/', {
      method: 'POST',
    })
  },

  markRead(notificationId: number | string) {
    return $api<Notification>(`/notifications/${notificationId}/mark_read/`, {
      method: 'POST',
    })
  },

  unreadCount() {
    return $api<UnreadCountResponse>('/notifications/unread_count/')
  },
}
