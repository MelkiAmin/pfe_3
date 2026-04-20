import { ofetch } from 'ofetch'
import { authSession } from '@/services/http/axios'

const apiBaseURL = import.meta.env.VITE_API_BASE_URL || '/api'
const RETRYABLE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS'])

type ApiRequestOptions = {
  _retried?: boolean
  _skipAuth?: boolean
}

const withHeaders = (headers?: HeadersInit) => new Headers(headers || {})

const getAccessToken = () => authSession.getTokens().access || useCookie<string | null>('accessToken').value
const getRefreshToken = () => authSession.getTokens().refresh || useCookie<string | null>('refreshToken').value

export const $api = ofetch.create({
  baseURL: apiBaseURL,
  async onRequest({ options }) {
    const requestOptions = options as typeof options & ApiRequestOptions
    const headers = withHeaders(options.headers)

    options.headers = headers

    if (requestOptions._skipAuth)
      return

    const accessToken = getAccessToken()
    if (accessToken)
      headers.set('Authorization', `Bearer ${accessToken}`)
  },
  async onResponseError(context) {
    const { request, options, response } = context
    const requestOptions = options as typeof options & ApiRequestOptions

    if (response.status !== 401 || requestOptions._retried)
      throw context.error

    if (requestOptions._skipAuth)
      throw context.error

    requestOptions._retried = true

    const refreshToken = getRefreshToken()
    if (refreshToken) {
      try {
        const refreshed = await ofetch<{ access?: string }>(`${apiBaseURL}/auth/token/refresh/`, {
          method: 'POST',
          body: { refresh: refreshToken },
        })

        if (refreshed.access) {
          authSession.setSession({
            access: refreshed.access,
            refresh: refreshToken,
          }, Boolean(localStorage.getItem('auth_access_token')))

          const retryHeaders = withHeaders(options.headers)
          retryHeaders.set('Authorization', `Bearer ${refreshed.access}`)

          return await ofetch(request, {
            ...options,
            headers: retryHeaders,
          })
        }
      }
      catch {
        authSession.clear()
      }
    }
    else {
      authSession.clear()
    }

    throw context.error
  },
})
