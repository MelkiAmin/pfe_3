import { setupLayouts } from 'virtual:meta-layouts'
import type { App } from 'vue'

import type { RouteRecordRaw } from 'vue-router/auto'

import { createRouter, createWebHistory } from 'vue-router/auto'
import { store } from '../2.pinia'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to) {
    if (to.hash)
      return { el: to.hash, behavior: 'smooth', top: 60 }

    return { top: 0 }
  },
  extendRoutes: pages => setupLayouts(pages as RouteRecordRaw[]),
})

router.beforeEach(async to => {
  const authStore = useAuthStore(store)
  authStore.bootstrap()

  const accessToken = authStore.accessToken
  const role = authStore.role as string
  const isAuthPage = to.path === '/login' || to.path === '/register'
  const isExplicitPublicPath = to.path === '/login'
    || to.path === '/register'
    || to.path === '/events'
    || to.path.startsWith('/events/')
    || to.path === '/tickets/verify'
    || to.path === '/'
  const isPublicRoute = Boolean(to.meta.public) || isExplicitPublicPath

  const adminOnly = to.path.startsWith('/admin')
  const organizerOnly = to.path.startsWith('/organizer')
  const allowedRoles = Array.isArray(to.meta.roles) ? to.meta.roles as string[] : null

  if (!accessToken && isAuthPage)
    return true

  if (!isPublicRoute && !accessToken) {
    if (to.path === '/login')
      return true

    return {
      path: '/login',
      query: { redirect: to.fullPath },
    }
  }

  if (isAuthPage && accessToken)
    return { path: authStore.dashboardRouteByRole(role) }

  if (adminOnly && role !== 'admin')
    return { path: '/' }

  if (organizerOnly && !['organizer', 'admin'].includes(role))
    return { path: '/' }

  if (allowedRoles && !allowedRoles.includes(role))
    return { path: authStore.dashboardRouteByRole(role) }
})

export { router }

export default function (app: App) {
  app.use(router)
}
