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

export type VerifyEmailPayload = {
  email: string
  code: string
}

export type RequestPasswordResetPayload = {
  email: string
}

export type ResetPasswordPayload = {
  email: string
  code: string
  new_password: string
}

export type ChangePasswordPayload = {
  old_password: string
  new_password: string
  new_password_confirm: string
}

export const authApi = {
  register(payload: RegisterPayload) {
    return $api<{ detail: string }>('/auth/register/', {
      method: 'POST',
      body: payload,
      _skipAuth: true,
    })
  },

  verifyEmail(payload: VerifyEmailPayload) {
    return $api<AuthResponse>('/auth/email/confirm-verification/', {
      method: 'POST',
      body: payload,
      _skipAuth: true,
    })
  },

  requestPasswordReset(payload: RequestPasswordResetPayload) {
    return $api<{ detail: string }>('/auth/password-reset/', {
      method: 'POST',
      body: payload,
      _skipAuth: true,
    })
  },

  resetPassword(payload: ResetPasswordPayload) {
    return $api<{ detail: string }>('/auth/password-reset/confirm/', {
      method: 'POST',
      body: payload,
      _skipAuth: true,
    })
  },

  login(payload: LoginPayload) {
    return $api<AuthResponse>('/auth/login/', {
      method: 'POST',
      body: payload,
      _skipAuth: true,
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

  listPendingOrganizers() {
    return $api<{ id: number; email: string; first_name: string; last_name: string; phone: string; created_at: string }[]>('/auth/organizers/pending/')
  },

  approveOrganizer(userId: number) {
    return $api<{ detail: string; approval_status: string }>(`/auth/organizers/${userId}/approve/`, {
      method: 'POST',
    })
  },

  rejectOrganizer(userId: number, note: string) {
    return $api<{ detail: string; approval_status: string }>(`/auth/organizers/${userId}/reject/`, {
      method: 'POST',
      body: { note },
    })
  },
}
