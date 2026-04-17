import { authApi } from '@/services/api'
import type { LoginPayload, RegisterPayload } from '@/services/api/auth.api'
import type { AuthResponse, AuthUser } from '@/services/api/types'

const extractErrorMessage = (error: unknown) => {
  const fallbackMessage = 'Something went wrong. Please try again.'

  if (!(error instanceof Error))
    return fallbackMessage

  const errorWithData = error as Error & { data?: Record<string, unknown> }
  const detail = errorWithData.data?.detail

  if (typeof detail === 'string')
    return detail

  if (typeof errorWithData.data === 'object' && errorWithData.data) {
    const firstEntry = Object.values(errorWithData.data)[0]

    if (typeof firstEntry === 'string')
      return firstEntry

    if (Array.isArray(firstEntry) && typeof firstEntry[0] === 'string')
      return firstEntry[0]
  }

  return error.message || fallbackMessage
}

export const useAuth = () => {
  const accessToken = useCookie<string | null>('accessToken')
  const refreshToken = useCookie<string | null>('refreshToken')
  const userData = useCookie<AuthUser | null>('userData')

  const setSession = (data: AuthResponse) => {
    accessToken.value = data.tokens.access
    refreshToken.value = data.tokens.refresh
    userData.value = data.user
  }

  const clearSession = () => {
    accessToken.value = null
    refreshToken.value = null
    userData.value = null
  }

  const login = async (payload: LoginPayload) => {
    const data = await authApi.login(payload)
    setSession(data)
    return data
  }

  const register = async (payload: RegisterPayload) => {
    const data = await authApi.register({
      role: 'attendee',
      ...payload,
    })
    setSession(data)
    return data
  }

  const logout = async () => {
    try {
      if (refreshToken.value)
        await authApi.logout(refreshToken.value)
    }
    catch {

    }
    finally {
      clearSession()
    }
  }

  return {
    login,
    register,
    logout,
    clearSession,
    extractErrorMessage,
  }
}
