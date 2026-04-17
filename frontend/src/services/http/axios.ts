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

export const apiClient = axios.create({
  baseURL: apiBase,
  timeout: 15000,
})

let isRefreshing = false
let pendingRequests: ((token: string | null) => void)[] = []

const flushQueue = (token: string | null) => {
  pendingRequests.forEach(cb => cb(token))
  pendingRequests = []
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

    if (status !== 401 || originalRequest?._retry)
      return Promise.reject(error)

    const { refresh } = authSession.getTokens()
    if (!refresh) {
      authSession.clear()
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise(resolve => {
        pendingRequests.push((token: string | null) => {
          if (token)
            originalRequest.headers.Authorization = `Bearer ${token}`
          resolve(apiClient(originalRequest))
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

      originalRequest.headers.Authorization = `Bearer ${access}`
      flushQueue(access)
      return apiClient(originalRequest)
    }
    catch (refreshError) {
      flushQueue(null)
      authSession.clear()
      return Promise.reject(refreshError)
    }
    finally {
      isRefreshing = false
    }
  },
)
