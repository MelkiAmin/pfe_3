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

      if (accessToken && userData) {
        this.accessToken = accessToken
        this.refreshToken = refreshToken
        this.user = userData
      } else {
        this.clearSession()
      }
    },

    clearSession() {
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      this.loading = false
      this.error = ''
      authSession.clear()
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
        const response = error?.response?.data
        const throttleMatch = error?.message?.match(/Expected available in (\d+) seconds/)
        
        if (throttleMatch || response?.detail?.includes('throttl')) {
          const seconds = throttleMatch ? Math.ceil(parseInt(throttleMatch[1]) / 1000) : 30
          this.error = `Trop de tentatives. Veuillez patienter ${seconds} secondes avant de réessayer.`
        }
        else if (response?.detail) {
          this.error = response.detail
        }
        else {
          this.error = 'Email ou mot de passe incorrect.'
        }
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
        this.clearSession()
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

    async requestPasswordReset(email: string) {
      this.loading = true
      this.error = ''
      try {
        const { data } = await apiClient.post('/auth/password-reset/', { email })
        return data
      }
      catch (error: any) {
        const detail = error?.response?.data?.detail || error?.message
        this.error = typeof detail === 'string' ? detail : 'Failed to send reset email.'
        throw new Error(this.error)
      }
      finally {
        this.loading = false
      }
    },

    async resetPassword(email: string, code: string, newPassword: string) {
      this.loading = true
      this.error = ''
      try {
        const { data } = await apiClient.post('/auth/password-reset/confirm/', {
          email,
          code,
          new_password: newPassword,
        })
        return data
      }
      catch (error: any) {
        const detail = error?.response?.data?.detail || error?.message
        this.error = typeof detail === 'string' ? detail : 'Failed to reset password.'
        throw new Error(this.error)
      }
      finally {
        this.loading = false
      }
    },
  },
})
