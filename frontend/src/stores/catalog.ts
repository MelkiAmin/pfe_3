import { defineStore } from 'pinia'
import { eventsApi } from '@/services/api'
import type { Category, EventListItem } from '@/services/api'

const EVENTS_KEY = 'catalog_recent_events'
const CATEGORIES_KEY = 'catalog_categories'

const read = <T>(key: string, fallback: T): T => {
  try {
    const value = localStorage.getItem(key)
    return value ? JSON.parse(value) as T : fallback
  }
  catch {
    return fallback
  }
}

export const useCatalogStore = defineStore('catalog', {
  state: () => ({
    recentEvents: read<EventListItem[]>(EVENTS_KEY, []),
    categories: read<Category[]>(CATEGORIES_KEY, []),
    loadedAt: 0,
  }),
  actions: {
    persist() {
      localStorage.setItem(EVENTS_KEY, JSON.stringify(this.recentEvents))
      localStorage.setItem(CATEGORIES_KEY, JSON.stringify(this.categories))
    },

    async load(force = false) {
      const now = Date.now()
      const isFresh = now - this.loadedAt < 60_000
      if (!force && isFresh && this.recentEvents.length && this.categories.length)
        return

      const [events, categories] = await Promise.all([
        eventsApi.list({ ordering: '-start_date' }),
        eventsApi.listCategories(),
      ])

      this.recentEvents = events
      this.categories = categories
      this.loadedAt = now
      this.persist()
    },
  },
})
