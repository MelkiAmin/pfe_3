import { defineStore } from 'pinia'
import { eventsApi } from '@/services/api'
import type { EventListItem, Category } from '@/services/api/types'
import type { EventListParams } from '@/services/api/events.api'

type EventsFilters = {
  search: string
  category: number | null
  event_type: string
  city: string
  is_free: boolean | null
  date_from: string
  date_to: string
  ordering: string
}

type SnackbarState = {
  show: boolean
  message: string
  color: 'success' | 'error' | 'warning' | 'info'
}

export const useCatalogStore = defineStore('catalog', {
  state: () => ({
    events: [] as EventListItem[],
    featuredEvents: [] as EventListItem[],
    categories: [] as Category[],
    loading: false,
    featuredLoading: false,
    categoriesLoading: false,
    totalItems: 0,
    page: 1,
    pageSize: 12,
    filters: {
      search: '',
      category: null,
      event_type: '',
      city: '',
      is_free: null,
      date_from: '',
      date_to: '',
      ordering: '-start_date',
    } as EventsFilters,
    snackbar: {
      show: false,
      message: '',
      color: 'success',
    } as SnackbarState,
  }),

  actions: {
    notify(message: string, color: SnackbarState['color'] = 'success') {
      this.snackbar = { show: true, message, color }
    },

    async fetchEvents(params?: Partial<EventsFilters> & { page?: number; pageSize?: number }) {
      this.loading = true

      const nextPage = params?.page ?? this.page
      const nextPageSize = params?.pageSize ?? this.pageSize

      this.page = nextPage
      this.pageSize = nextPageSize

      if (params) {
        this.filters = { ...this.filters, ...params }
      }

      try {
        const apiParams: EventListParams = {
          page: nextPage,
          page_size: nextPageSize,
          search: this.filters.search || undefined,
          category: this.filters.category || undefined,
          event_type: this.filters.event_type || undefined,
          city: this.filters.city || undefined,
          is_free: this.filters.is_free ?? undefined,
          date_from: this.filters.date_from || undefined,
          date_to: this.filters.date_to || undefined,
          ordering: this.filters.ordering || undefined,
        }

        const response = await eventsApi.list(apiParams)
        this.events = response.results
        this.totalItems = response.count
      }
      catch (error: any) {
        this.events = []
        this.totalItems = 0
        this.notify(error?.data?.detail || error?.message || 'Impossible de charger les evenements.', 'error')
      }
      finally {
        this.loading = false
      }
    },

    async fetchFeaturedEvents() {
      this.featuredLoading = true
      try {
        const response = await eventsApi.listFeatured(6)
        this.featuredEvents = Array.isArray(response) ? response : []
      }
      catch (error: any) {
        console.error('Failed to fetch featured events:', error)
        this.featuredEvents = []
      }
      finally {
        this.featuredLoading = false
      }
    },

    async fetchCategories() {
      this.categoriesLoading = true
      try {
        const response = await eventsApi.listCategories()
        this.categories = response.results
      }
      catch (error: any) {
        this.categories = []
      }
      finally {
        this.categoriesLoading = false
      }
    },

    setFilter<K extends keyof EventsFilters>(key: K, value: EventsFilters[K]) {
      this.filters[key] = value
      this.page = 1
      this.fetchEvents()
    },

    resetFilters() {
      this.filters = {
        search: '',
        category: null,
        event_type: '',
        city: '',
        is_free: null,
        date_from: '',
        date_to: '',
        ordering: '-start_date',
      }
      this.page = 1
      this.fetchEvents()
    },
  },
})
