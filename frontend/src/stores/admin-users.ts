import { defineStore } from 'pinia'
import { adminPanelApi } from '@/services/api'
import type { AdminUser, AdminUserStatus, UserRole } from '@/services/api'

type AdminUsersFilters = {
  search: string
  role: UserRole | ''
  status: AdminUserStatus | ''
}

type SnackbarState = {
  show: boolean
  message: string
  color: 'success' | 'error' | 'warning' | 'info'
}

type FetchUsersParams = Partial<AdminUsersFilters> & {
  page?: number
  pageSize?: number
}

type UpdateUserPayload = {
  email?: string
  first_name?: string
  last_name?: string
  phone?: string
  role?: UserRole
  status?: AdminUserStatus
}

export const useAdminUsersStore = defineStore('admin-users', {
  state: () => ({
    users: [] as AdminUser[],
    selectedUser: null as AdminUser | null,
    loading: false,
    saving: false,
    deleting: false,
    totalItems: 0,
    page: 1,
    pageSize: 10,
    filters: {
      search: '',
      role: '',
      status: '',
    } as AdminUsersFilters,
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

    async fetchUsers(params: FetchUsersParams = {}) {
      this.loading = true

      const nextPage = params.page ?? this.page
      const nextPageSize = params.pageSize ?? this.pageSize
      this.page = nextPage
      this.pageSize = nextPageSize
      this.filters = {
        search: params.search ?? this.filters.search,
        role: params.role ?? this.filters.role,
        status: params.status ?? this.filters.status,
      }

      try {
        const response = await adminPanelApi.listUsers({
          page: nextPage,
          page_size: nextPageSize,
          search: this.filters.search || undefined,
          role: this.filters.role || undefined,
          status: this.filters.status || undefined,
        })

        this.users = response.results
        this.totalItems = response.count
      }
      catch (error: any) {
        this.users = []
        this.totalItems = 0
        this.notify(error?.data?.detail || error?.message || 'Impossible de charger les utilisateurs.', 'error')
      }
      finally {
        this.loading = false
      }
    },

    async updateUser(userId: number, payload: UpdateUserPayload) {
      this.saving = true
      try {
        const updatedUser = await adminPanelApi.updateUser(userId, payload)
        this.users = this.users.map(user => user.id === userId ? updatedUser : user)
        if (this.selectedUser?.id === userId)
          this.selectedUser = updatedUser
        this.notify('Utilisateur mis a jour avec succes.')
        return updatedUser
      }
      catch (error: any) {
        this.notify(error?.data?.detail || error?.message || 'Impossible de mettre a jour cet utilisateur.', 'error')
        throw error
      }
      finally {
        this.saving = false
      }
    },

    async deleteUser(userId: number) {
      this.deleting = true
      try {
        await adminPanelApi.removeUser(userId)
        this.notify('Compte desactive avec succes.')
        await this.fetchUsers()
      }
      catch (error: any) {
        this.notify(error?.data?.detail || error?.message || 'Impossible de desactiver cet utilisateur.', 'error')
        throw error
      }
      finally {
        this.deleting = false
      }
    },

    async banUser(userId: number, reason: string) {
      this.saving = true
      try {
        await adminPanelApi.banUser(userId, reason)
        this.notify('Utilisateur banni avec succes.', 'warning')
        await this.fetchUsers()
      }
      catch (error: any) {
        this.notify(error?.data?.detail || error?.message || 'Impossible de bannir cet utilisateur.', 'error')
        throw error
      }
      finally {
        this.saving = false
      }
    },

    async unbanUser(userId: number) {
      this.saving = true
      try {
        await adminPanelApi.unbanUser(userId)
        this.notify('Utilisateur reactive avec succes.')
        await this.fetchUsers()
      }
      catch (error: any) {
        this.notify(error?.data?.detail || error?.message || 'Impossible de reactiver cet utilisateur.', 'error')
        throw error
      }
      finally {
        this.saving = false
      }
    },
  },
})
