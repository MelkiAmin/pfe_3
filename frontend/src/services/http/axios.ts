import axios from 'axios'

type TokenPair = {
  access: string | null
  refresh: string | null
}

const ACCESS_KEY = 'auth_access_token'
const REFRESH_KEY = 'auth_refresh_token'
const USER_KEY = 'auth_user'

const readStorage = (key: string) => localStorage.getItem(key) || sessionStorage.getItem(key)

export const authSession = {
  getTokens(): TokenPair {
    return {
      access: readStorage(ACCESS_KEY),
      refresh: readStorage(REFRESH_KEY),
    }
  },

  setSession(data: { access: string; refresh: string; user?: unknown }, remember = true) {
    const storage = remember ? localStorage : sessionStorage
    const otherStorage = remember ? sessionStorage : localStorage

    storage.setItem(ACCESS_KEY, data.access)
    storage.setItem(REFRESH_KEY, data.refresh)
    if (data.user)
      storage.setItem(USER_KEY, JSON.stringify(data.user))

    otherStorage.removeItem(ACCESS_KEY)
    otherStorage.removeItem(REFRESH_KEY)
    otherStorage.removeItem(USER_KEY)

    useCookie<string | null>('accessToken').value = data.access
    useCookie<string | null>('refreshToken').value = data.refresh
    if (data.user)
      useCookie('userData').value = data.user as any
  },

  clear() {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
    localStorage.removeItem(USER_KEY)
    sessionStorage.removeItem(ACCESS_KEY)
    sessionStorage.removeItem(REFRESH_KEY)
    sessionStorage.removeItem(USER_KEY)

    useCookie<string | null>('accessToken').value = null
    useCookie<string | null>('refreshToken').value = null
    useCookie<any>('userData').value = null
  },
}

const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
const AUTH_ENDPOINT_PATTERN = /\/auth\/(login|register|logout|token\/refresh)\/?$/

export const apiClient = axios.create({
  baseURL: apiBase,
  timeout: 15000,
})

let isRefreshing = false
let pendingRequests: Array<{
  resolve: (token: string) => void
  reject: (error: unknown) => void
}> = []

const flushQueue = (token: string) => {
  pendingRequests.forEach(({ resolve }) => resolve(token))
  pendingRequests = []
}

const rejectQueue = (error: unknown) => {
  pendingRequests.forEach(({ reject }) => reject(error))
  pendingRequests = []
}

const isAuthEndpoint = (url?: string) =>
  typeof url === 'string' && AUTH_ENDPOINT_PATTERN.test(url)

const redirectToLogin = () => {
  if (typeof window === 'undefined')
    return

  const { pathname, search, hash, origin } = window.location
  if (pathname.endsWith('/login') || pathname.endsWith('/register'))
    return

  const loginUrl = new URL('login', new URL(import.meta.env.BASE_URL || '/', origin))
  loginUrl.searchParams.set('redirect', `${pathname}${search}${hash}`)
  window.location.replace(loginUrl.toString())
}

apiClient.interceptors.request.use(config => {
  const { access } = authSession.getTokens()
  if (access)
    config.headers.Authorization = `Bearer ${access}`
  return config
})

apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    const status = error?.response?.status
    const requestUrl = originalRequest?.url as string | undefined

    if (status !== 401 || originalRequest?._retry || isAuthEndpoint(requestUrl))
      return Promise.reject(error)

    const { refresh } = authSession.getTokens()
    if (!refresh) {
      authSession.clear()
      redirectToLogin()
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingRequests.push({
          resolve: (token: string) => {
            originalRequest._retry = true
            originalRequest.headers = originalRequest.headers || {}
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(apiClient(originalRequest))
          },
          reject,
        })
      })
    }

    originalRequest._retry = true
    isRefreshing = true

    try {
      const res = await axios.post(`${apiBase}/auth/token/refresh/`, { refresh })
      const access = res.data?.access as string
      if (!access)
        throw new Error('No access token returned.')

      const current = authSession.getTokens()
      authSession.setSession({
        access,
        refresh: current.refresh || refresh,
      }, Boolean(localStorage.getItem(ACCESS_KEY)))

      originalRequest.headers = originalRequest.headers || {}
      originalRequest.headers.Authorization = `Bearer ${access}`
      flushQueue(access)
      return apiClient(originalRequest)
    }
    catch (refreshError) {
      rejectQueue(refreshError)
      authSession.clear()
      redirectToLogin()
      return Promise.reject(refreshError)
    }
    finally {
      isRefreshing = false
    }
  },
)
