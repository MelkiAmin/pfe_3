import { $api } from '@/utils/api'
import { unwrapListResponse } from './list-response'
import type { OrganizerDashboard, OrganizerProfile } from './types'
import type { ListResponse } from './list-response'

export type OrganizerProfilePayload = {
  organization_name?: string
  bio?: string
  logo?: File | null
  website?: string
  social_links?: Record<string, string>
}

export const organizerApi = {
  getProfile() {
    return $api<OrganizerProfile>('/organizer/profile/')
  },

  updateProfile(payload: OrganizerProfilePayload | FormData) {
    return $api<OrganizerProfile>('/organizer/profile/', {
      method: 'PATCH',
      body: payload,
    })
  },

  listVerified() {
    return $api<ListResponse<OrganizerProfile>>('/organizer/list/').then(unwrapListResponse)
  },

  getDashboard() {
    return $api<OrganizerDashboard>('/organizer/dashboard/')
  },
}
