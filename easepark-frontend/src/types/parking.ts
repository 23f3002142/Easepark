export interface ParkingLot {
  id: number
  name: string
  parking_name?: string
  address: string
  price: number
  pin_code: string
  max_spots: number
  latitude?: number
  longitude?: number
  is_active?: boolean
  total_spots?: number
  free_spots?: number
  occupied_spots?: number
  available_spots?: number
}

export interface ParkingSpot {
  id: number
  lot_id: number
  spot_number: string
  status: 'A' | 'O'
  is_active: boolean
}

export interface Reservation {
  id: number
  lot_name: string
  spot_number: string
  vehicle_number: string
  booking_timestamp: string
  releasing_timestamp?: string | null
  total_cost?: number | null
  status: 'pending' | 'active' | 'completed' | 'cancelled'
  reservation_id?: number
  date?: string
  time_range?: string
}

export interface Payment {
  id: number
  reservation_id: number
  razorpay_payment_id: string
  razorpay_order_id: string
  amount: number
  status: 'success' | 'failed'
}

export interface Pagination {
  page: number
  per_page: number
  total_pages: number
  total_items: number
}
