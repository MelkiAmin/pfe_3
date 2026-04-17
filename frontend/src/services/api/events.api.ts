import { $api } from '@/utils/api'
import type {
  Category,
  EventDetail,
  EventListItem,
  EventPayload,
  EventReview,
  EventStatus,
  EventType,
  FavoriteEvent,
} from './types'

export type EventListParams = {
  status?: EventStatus
  event_type?: EventType
  category?: number
  city?: string
  is_free?: boolean
  search?: string
  ordering?: 'start_date' | '-start_date' | 'created_at' | '-created_at' | 'title' | '-title'
}

export const eventsApi = {
  list(params?: EventListParams) {
    return $api<EventListItem[]>('/events/', { query: params })
  },

  getById(eventId: number | string) {
    return $api<EventDetail>(`/events/${eventId}/`)
  },

  create(payload: EventPayload | FormData) {
    return $api<EventDetail>('/events/', {
      method: 'POST',
      body: payload,
    })
  },

  update(eventId: number | string, payload: Partial<EventPayload> | FormData) {
    return $api<EventDetail>(`/events/${eventId}/`, {
      method: 'PATCH',
      body: payload,
    })
  },

  remove(eventId: number | string) {
    return $api<void>(`/events/${eventId}/`, { method: 'DELETE' })
  },

  listCategories() {
    return $api<Category[]>('/events/categories/')
  },

  getCategory(categoryId: number | string) {
    return $api<Category>(`/events/categories/${categoryId}/`)
  },

  createCategory(payload: Omit<Category, 'id'>) {
    return $api<Category>('/events/categories/', {
      method: 'POST',
      body: payload,
    })
  },

  updateCategory(categoryId: number | string, payload: Partial<Omit<Category, 'id'>>) {
    return $api<Category>(`/events/categories/${categoryId}/`, {
      method: 'PATCH',
      body: payload,
    })
  },

  removeCategory(categoryId: number | string) {
    return $api<void>(`/events/categories/${categoryId}/`, { method: 'DELETE' })
  },

  listFavorites() {
    return $api<FavoriteEvent[]>('/events/favorites/')
  },

  addFavorite(eventId: number) {
    return $api<FavoriteEvent>('/events/favorites/', {
      method: 'POST',
      body: { event: eventId },
    })
  },

  removeFavorite(favoriteId: number | string) {
    return $api<void>(`/events/favorites/${favoriteId}/`, {
      method: 'DELETE',
    })
  },

  listReviews(params?: { event?: number }) {
    return $api<EventReview[]>('/events/reviews/', { query: params })
  },

  createReview(payload: { event: number; rating: number; comment?: string }) {
    return $api<EventReview>('/events/reviews/', {
      method: 'POST',
      body: payload,
    })
  },

  updateReview(reviewId: number | string, payload: { rating?: number; comment?: string }) {
    return $api<EventReview>(`/events/reviews/${reviewId}/`, {
      method: 'PATCH',
      body: payload,
    })
  },

  deleteReview(reviewId: number | string) {
    return $api<void>(`/events/reviews/${reviewId}/`, {
      method: 'DELETE',
    })
  },
}
