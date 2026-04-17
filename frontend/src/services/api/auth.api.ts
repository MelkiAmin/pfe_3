import { $api } from '@/utils/api'
import type { AuthResponse, AuthUser, AuthTokens } from './types'

export type LoginPayload = {
  email: string
  password: string
}

export type RegisterPayload = {
  email: string
  first_name: string
  last_name: string
  password: string
  password_confirm: string
  role?: 'attendee' | 'organizer' | 'admin'
  phone?: string
}

export type ChangePasswordPayload = {
  old_password: string
  new_password: string
  new_password_confirm: string
}

export const authApi = {
  register(payload: RegisterPayload) {
    return $api<AuthResponse>('/auth/register/', {
      method: 'POST',
      body: payload,
    })
  },

  login(payload: LoginPayload) {
    return $api<AuthResponse>('/auth/login/', {
      method: 'POST',
      body: payload,
    })
  },

  logout(refresh: string) {
    return $api<{ detail: string }>('/auth/logout/', {
      method: 'POST',
      body: { refresh },
    })
  },

  refreshToken(refresh: string) {
    return $api<Pick<AuthTokens, 'access'>>('/auth/token/refresh/', {
      method: 'POST',
      body: { refresh },
    })
  },

  getProfile() {
    return $api<AuthUser>('/auth/profile/')
  },

  updateProfile(payload: Partial<AuthUser>) {
    return $api<AuthUser>('/auth/profile/', {
      method: 'PATCH',
      body: payload,
    })
  },

  changePassword(payload: ChangePasswordPayload) {
    return $api<{ detail: string }>('/auth/change-password/', {
      method: 'POST',
      body: payload,
    })
  },
}
