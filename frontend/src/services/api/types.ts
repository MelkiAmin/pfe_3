export type UserRole = 'attendee' | 'organizer' | 'admin'

export type AuthTokens = {
  access: string
  refresh: string
}

export type AuthUser = {
  id: number
  email: string
  first_name: string
  last_name: string
  full_name: string
  role: UserRole
  avatar: string | null
  phone: string
  is_email_verified: boolean
  created_at: string
}

export type AuthResponse = {
  user: AuthUser
  tokens: AuthTokens
}

export type Category = {
  id: number
  name: string
  slug: string
  description: string
  icon: string
}

export type EventStatus = 'draft' | 'published' | 'cancelled' | 'completed'
export type EventType = 'in_person' | 'online' | 'hybrid'

export type EventListItem = {
  id: number
  title: string
  slug: string
  cover_image: string | null
  event_type: EventType
  status: EventStatus
  category: Category | null
  organizer_name: string
  start_date: string
  end_date: string
  city: string
  country: string
  is_free: boolean
  tickets_sold: number
  is_sold_out: boolean
  average_rating: number
  reviews_count: number
}

export type EventDetail = {
  id: number
  organizer: AuthUser
  category: Category | null
  title: string
  slug: string
  description: string
  cover_image: string | null
  event_type: EventType
  status: EventStatus
  venue_name: string
  address: string
  city: string
  country: string
  online_url: string
  start_date: string
  end_date: string
  max_capacity: number | null
  is_free: boolean
  tags: string[]
  created_at: string
  updated_at: string
  tickets_sold: number
  is_sold_out: boolean
  average_rating: number
  reviews_count: number
}

export type EventPayload = {
  category?: number | null
  title: string
  description: string
  cover_image?: File | null
  event_type?: EventType
  status?: EventStatus
  venue_name?: string
  address?: string
  city?: string
  country?: string
  online_url?: string
  start_date: string
  end_date: string
  max_capacity?: number | null
  is_free?: boolean
  tags?: string[]
}

export type OrganizerProfile = {
  id: number
  user_name: string
  user_email: string
  organization_name: string
  bio: string
  logo: string | null
  website: string
  social_links: Record<string, string>
  is_verified: boolean
  total_events: number
  created_at: string
}

export type OrganizerDashboard = {
  total_events: number
  published_events: number
  total_tickets_sold: number
}

export type TicketStatus = 'pending' | 'confirmed' | 'cancelled' | 'used' | 'refunded'

export type TicketType = {
  id: number
  event: number
  name: string
  description: string
  price: string
  quantity: number
  quantity_sold: number
  available_quantity: number
  is_available: boolean
  sale_start: string | null
  sale_end: string | null
}

export type Ticket = {
  id: number
  ticket_number: string
  ticket_type: number
  ticket_type_name: string
  event: number
  event_title: string
  attendee: number
  attendee_name: string
  status: TicketStatus
  price_paid: string
  qr_code: string | null
  checked_in_at: string | null
  created_at: string
}

export type PaymentStatus = 'pending' | 'completed' | 'failed' | 'refunded'
export type PaymentProvider = 'stripe' | 'paypal' | 'free'

export type Payment = {
  id: number
  event: number | null
  amount: string
  currency: string
  status: PaymentStatus
  provider: PaymentProvider
  provider_payment_id: string
  created_at: string
}

export type CheckoutSessionPayload = {
  ticket_type_id: number
  quantity: number
  success_url: string
  cancel_url: string
}

export type CheckoutSessionResponse = {
  session_id: string
  checkout_url: string
  payment_id: number
}

export type NotificationType =
  | 'ticket_purchased'
  | 'event_reminder'
  | 'event_cancelled'
  | 'event_updated'
  | 'payment_confirmed'
  | 'payment_failed'
  | 'general'

export type Notification = {
  id: number
  notification_type: NotificationType
  title: string
  message: string
  data: Record<string, unknown>
  is_read: boolean
  created_at: string
}

export type UnreadCountResponse = {
  unread_count: number
}

export type FavoriteEvent = {
  id: number
  event: number
  event_title: string
  created_at: string
}

export type EventReview = {
  id: number
  event: number
  user: number
  user_name: string
  rating: number
  comment: string
  created_at: string
  updated_at: string
}

export type AdminDashboardStats = {
  total_users: number
  total_organizers: number
  total_events: number
  published_events: number
  total_tickets_sold: number
  total_revenue: number
}
