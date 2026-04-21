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
        console.log('Updating user:', userId, 'payload:', payload)
        const response = await adminPanelApi.updateUser(userId, payload)
        console.log('Update response:', response)

        if (!response || !response.id) {
          throw new Error('Invalid response from server')
        }

        this.users = this.users.map(user => user.id === userId ? response : user)
        if (this.selectedUser?.id === userId)
          this.selectedUser = response

        this.notify('Utilisateur mis a jour avec succes.')
        return response
      }
      catch (error: any) {
        console.error('Update error:', error)
        const message = error?.response?.data?.detail || error?.message || 'Impossible de mettre a jour cet utilisateur.'
        this.notify(message, 'error')
        throw error
      }
      finally {
        this.saving = false
      }
    },

    async deleteUser(userId: number) {
      this.deleting = true
      try {
        console.log('Deleting user:', userId)
        await adminPanelApi.removeUser(userId)
        this.notify('Compte desactive avec succes.')
        await this.fetchUsers()
      }
      catch (error: any) {
        console.error('Delete error:', error)
        this.notify(error?.response?.data?.detail || error?.message || 'Impossible de desactiver cet utilisateur.', 'error')
        throw error
      }
      finally {
        this.deleting = false
      }
    },

    async banUser(userId: number, reason: string) {
      this.saving = true
      try {
        console.log('Banning user:', userId, 'reason:', reason)
        const result = await adminPanelApi.banUser(userId, reason)
        console.log('Ban result:', result)
        this.notify('Utilisateur banni avec succes.', 'warning')
        await this.fetchUsers()
      }
      catch (error: any) {
        console.error('Ban error:', error)
        this.notify(error?.response?.data?.detail || error?.message || 'Impossible de bannir cet utilisateur.', 'error')
        throw error
      }
      finally {
        this.saving = false
      }
    },

    async unbanUser(userId: number) {
      this.saving = true
      try {
        const userIdNum = Number(userId)
        console.log('Calling unbanUser with ID:', userIdNum, 'type:', typeof userIdNum)

        const result = await adminPanelApi.unbanUser(userIdNum)
        console.log('Unban result:', result)

        this.notify('Utilisateur reactive avec succes.')
        await this.fetchUsers()
      }
      catch (error: any) {
        console.error('Unban error full:', JSON.stringify(error, null, 2))
        const message = error?.response?.data?.detail || error?.message || 'Erreur lors de la reactivation'
        this.notify(message, 'error')
        throw error
      }
      finally {
        this.saving = false
      }
    },
  },
})
