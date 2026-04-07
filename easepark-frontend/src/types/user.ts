export interface User {
  id: number
  username: string
  email: string
  role: 'user' | 'admin'
  full_name?: string
  phone_number?: string
  address?: string
  pin_code?: string
  member_since: string | null
  total_bookings: number
}
