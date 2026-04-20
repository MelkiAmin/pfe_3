import { defineStore } from 'pinia'
import { apiClient, authSession } from '@/services/http/axios'

type UserRole = 'attendee' | 'organizer' | 'admin'

type AuthUser = {
  id: number
  email: string
  first_name: string
  last_name: string
  role: UserRole
}

type LoginPayload = {
  email: string
  password: string
  rememberMe: boolean
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as AuthUser | null,
    accessToken: null as string | null,
    refreshToken: null as string | null,
    loading: false,
    error: '',
  }),
  getters: {
    isAuthenticated: state => Boolean(state.accessToken),
    role: state => state.user?.role || 'attendee',
  },
  actions: {
    bootstrap() {
      const accessToken = useCookie<string | null>('accessToken').value
      const refreshToken = useCookie<string | null>('refreshToken').value
      const userData = useCookie<AuthUser | null>('userData').value

      this.accessToken = accessToken
      this.refreshToken = refreshToken
      this.user = userData
    },

    async login(payload: LoginPayload) {
      this.loading = true
      this.error = ''

      try {
        const { data } = await apiClient.post('/auth/login/', {
          email: payload.email,
          password: payload.password,
        })

        this.user = data.user
        this.accessToken = data.tokens.access
        this.refreshToken = data.tokens.refresh

        authSession.setSession({
          access: data.tokens.access,
          refresh: data.tokens.refresh,
          user: data.user,
        }, payload.rememberMe)

        return data.user as AuthUser
      }
      catch (error: any) {
        const detail = error?.response?.data?.detail
        this.error = typeof detail === 'string' ? detail : 'Email ou mot de passe incorrect.'
        throw new Error(this.error)
      }
      finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        if (this.refreshToken)
          await apiClient.post('/auth/logout/', { refresh: this.refreshToken })
      }
      catch {

      }
      finally {
        this.$reset()
        authSession.clear()
      }
    },

    dashboardRouteByRole(role?: UserRole) {
      const safeRole = role || this.role
      if (safeRole === 'organizer')
        return '/organizer/dashboard'
      if (safeRole === 'admin')
        return '/admin/dashboard'
      return '/'
    },

    roleLabel(role?: UserRole) {
      const safeRole = role || this.role
      if (safeRole === 'organizer')
        return 'Organisateur'
      if (safeRole === 'admin')
        return 'Admin'
      return 'Utilisateur'
    },
  },
})
