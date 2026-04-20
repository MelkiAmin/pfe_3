import { defineStore } from 'pinia'
import { adminPanelApi } from '@/services/api'
import type { OrganizerProfile } from '@/services/api'
import type { AdminOrganizerListParams, AdminOrganizerUpdatePayload, AdminOrganizerStats } from '@/services/api/admin-panel.api'
import type { EventListItem } from '@/services/api/types'

type AdminOrganizersFilters = {
  search: string
  is_verified: boolean | ''
}

type SnackbarState = {
  show: boolean
  message: string
  color: 'success' | 'error' | 'warning' | 'info'
}

type FetchOrganizersParams = Partial<AdminOrganizersFilters> & {
  page?: number
  pageSize?: number
}

export const useAdminOrganizersStore = defineStore('admin-organizers', {
  state: () => ({
    organizers: [] as OrganizerProfile[],
    selectedOrganizer: null as OrganizerProfile | null,
    selectedOrganizerStats: null as AdminOrganizerStats | null,
    selectedOrganizerEvents: [] as EventListItem[],
    loading: false,
    saving: false,
    deleting: false,
    totalItems: 0,
    page: 1,
    pageSize: 10,
    filters: {
      search: '',
      is_verified: '',
    } as AdminOrganizersFilters,
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

    async fetchOrganizers(params: FetchOrganizersParams = {}) {
      this.loading = true

      const nextPage = params.page ?? this.page
      const nextPageSize = params.pageSize ?? this.pageSize
      this.page = nextPage
      this.pageSize = nextPageSize
      this.filters = {
        search: params.search ?? this.filters.search,
        is_verified: params.is_verified ?? this.filters.is_verified,
      }

      try {
        const response = await adminPanelApi.listOrganizers({
          page: nextPage,
          page_size: nextPageSize,
          search: this.filters.search || undefined,
          is_verified: this.filters.is_verified === '' ? undefined : this.filters.is_verified,
        })

        this.organizers = response.results
        this.totalItems = response.count
      }
      catch (error: any) {
        this.organizers = []
        this.totalItems = 0
        this.notify(error?.data?.detail || error?.message || 'Impossible de charger les organisateurs.', 'error')
      }
      finally {
        this.loading = false
      }
    },

    async fetchOrganizerDetails(organizerId: number) {
      this.loading = true
      try {
        const [organizer, stats, events] = await Promise.all([
          adminPanelApi.getOrganizer(organizerId),
          adminPanelApi.getOrganizerStats(organizerId),
          adminPanelApi.listOrganizerEvents(organizerId),
        ])

        this.selectedOrganizer = organizer
        this.selectedOrganizerStats = stats
        this.selectedOrganizerEvents = events
      }
      catch (error: any) {
        this.notify(error?.data?.detail || error?.message || 'Impossible de charger les details de l\'organisateur.', 'error')
      }
      finally {
        this.loading = false
      }
    },

    async updateOrganizer(organizerId: number, payload: AdminOrganizerUpdatePayload) {
      this.saving = true
      try {
        const updatedOrganizer = await adminPanelApi.updateOrganizer(organizerId, payload)
        this.organizers = this.organizers.map(org => org.id === organizerId ? updatedOrganizer : org)
        if (this.selectedOrganizer?.id === organizerId)
          this.selectedOrganizer = updatedOrganizer
        this.notify('Organisateur mis a jour avec succes.')
        return updatedOrganizer
      }
      catch (error: any) {
        this.notify(error?.data?.detail || error?.message || 'Impossible de mettre a jour cet organisateur.', 'error')
        throw error
      }
      finally {
        this.saving = false
      }
    },

    async deleteOrganizer(organizerId: number) {
      this.deleting = true
      try {
        await adminPanelApi.removeOrganizer(organizerId)
        this.notify('Compte organiseur desactive avec succes.')
        await this.fetchOrganizers()
      }
      catch (error: any) {
        this.notify(error?.data?.detail || error?.message || 'Impossible de desactiver cet organisateur.', 'error')
        throw error
      }
      finally {
        this.deleting = false
      }
    },

    clearSelectedOrganizer() {
      this.selectedOrganizer = null
      this.selectedOrganizerStats = null
      this.selectedOrganizerEvents = []
    },
  },
})
