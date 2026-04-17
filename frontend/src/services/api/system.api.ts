import { $api } from '@/utils/api'

export type HealthResponse = {
  status: string
  service: string
  timestamp: string
}

export const systemApi = {
  health() {
    return $api<HealthResponse>('/health/')
  },
}
