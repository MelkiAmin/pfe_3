import {
  adminPanelApi,
  authApi,
  eventsApi,
  notificationsApi,
  organizerApi,
  paymentsApi,
  systemApi,
  ticketsApi,
} from '@/services/api'

export const useBackendApi = () => ({
  adminPanelApi,
  authApi,
  eventsApi,
  notificationsApi,
  organizerApi,
  paymentsApi,
  systemApi,
  ticketsApi,
})
