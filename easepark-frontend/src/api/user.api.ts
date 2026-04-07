import api from './axios'
import type { Reservation, Pagination, ParkingLot } from '@/types/parking'
import type { User } from '@/types/user'

export interface DashboardData {
  user: User
  active_bookings: Array<{
    reservation_id: number
    lot_name: string
    spot_number: string
    date: string
    time_range: string
  }>
  available_lots: Array<{
    id: number
    name: string
    free_spots: number
    total_spots: number
  }>
  chart_labels: string[]
  chart_data: number[]
  notifications: string[]
}

export interface LotsResponse {
  lots: ParkingLot[]
  pagination: Pagination
}

export interface HistoryResponse {
  history: Reservation[]
  pagination: Pagination
}

export interface ReleaseInfo {
  reservation_id: number
  lot_name: string
  spot_number: string
  vehicle_number: string
  booking_time: string
  current_time: string
  duration_hours: number
  estimated_cost: number
  cost_per_hour: number
}

export interface ReleasePaymentData {
  order_id: string
  razorpay_key_id: string
  amount: number
  amount_paise: number
  reservation_id: number
  lot_name: string
  duration_hours: number
  user_name: string
  user_email: string
  user_phone: string
}

export interface SummaryData {
  user: User
  total_amount_paid: number
  total_duration_hours: number
  total_bookings: number
  first_booking: string | null
  latest_booking: string | null
  chart_labels: string[]
  chart_data: number[]
  chart_duration_labels: string[]
  chart_duration_data: number[]
  chart_booking_labels: string[]
  chart_duration_data_each: number[]
  chart_cost_data_each: number[]
  history: Reservation[]
  pagination: Pagination
}

export async function getDashboard(): Promise<DashboardData> {
  const { data } = await api.get('/user/dashboard')
  return data
}

export async function getProfile(): Promise<{ user: User }> {
  const { data } = await api.get('/user/profile')
  return data
}

export async function updateProfile(payload: Partial<User>): Promise<{ message: string; user: User }> {
  const { data } = await api.put('/user/profile', payload)
  return data
}

export async function getLots(params: { search?: string; page?: number; per_page?: number }): Promise<LotsResponse> {
  const { data } = await api.get('/user/lots', { params })
  return data
}

export async function getAllLots(): Promise<{ lots: ParkingLot[] }> {
  const { data } = await api.get('/user/lots/all')
  return data
}

export interface NearbyLot {
  id: number
  name: string
  address: string
  price: number
  latitude: number
  longitude: number
  max_spots: number
  free_spots: number
  distance_km: number
}

export async function getNearbyLots(lat: number, lng: number, limit = 5): Promise<{ lots: NearbyLot[] }> {
  const { data } = await api.get('/user/lots/nearby', { params: { lat, lng, limit } })
  return data
}

export async function reserveSpot(lotId: number, vehicleNumber: string): Promise<{
  message: string
  reservation_id: number
  spot_number: string
}> {
  const { data } = await api.post(`/user/book/${lotId}`, { vehicle_number: vehicleNumber })
  return data
}

export async function sendReleaseOtp(reservationId: number): Promise<{ message: string }> {
  const { data } = await api.post(`/user/release/${reservationId}/send-otp`)
  return data
}

export async function verifyReleaseOtp(reservationId: number, otp: string): Promise<{ message: string }> {
  const { data } = await api.post(`/user/release/${reservationId}/verify-otp`, { otp })
  return data
}

export async function verifyReleasePassword(reservationId: number, password: string): Promise<{ message: string }> {
  const { data } = await api.post(`/user/release/${reservationId}/verify-password`, { password })
  return data
}

export async function cancelRelease(reservationId: number): Promise<{ message: string }> {
  const { data } = await api.post(`/user/release/${reservationId}/cancel`)
  return data
}

export async function cancelBooking(reservationId: number): Promise<{ message: string }> {
  const { data } = await api.post(`/user/cancel/${reservationId}`)
  return data
}

export async function getHistory(params: { page?: number; per_page?: number }): Promise<HistoryResponse> {
  const { data } = await api.get('/user/history', { params })
  return data
}

export async function getReleaseInfo(reservationId: number): Promise<ReleaseInfo> {
  const { data } = await api.get(`/user/release/${reservationId}`)
  return data
}

export async function releaseSpot(reservationId: number): Promise<ReleasePaymentData> {
  const { data } = await api.post(`/user/release/${reservationId}`)
  return data
}

export async function releaseSpotFree(reservationId: number): Promise<{ message: string; total_cost: number; duration_hours: number }> {
  const { data } = await api.post(`/user/release/${reservationId}/confirm-free`)
  return data
}

export async function verifyPayment(payload: {
  payment_id: string
  order_id: string
  signature: string
  reservation_id: number
}): Promise<{ message: string; total_cost: number }> {
  const { data } = await api.post('/user/payment/verify', payload)
  return data
}

export function getReceiptUrl(reservationId: number): string {
  const token = localStorage.getItem('token')
  return `/api/user/receipt/${reservationId}?token=${token}`
}

export async function downloadHistoryCsv(): Promise<void> {
  const response = await api.get('/user/history/csv', { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'easepark_bookings.csv')
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export async function getSummary(params: { page?: number }): Promise<SummaryData> {
  const { data } = await api.get('/user/summary', { params })
  return data
}

export async function downloadSummaryReport(fromDate: string, toDate: string): Promise<void> {
  const response = await api.get('/user/summary/report', {
    params: { from: fromDate, to: toDate },
    responseType: 'blob',
  })
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `easepark_report_${fromDate}_to_${toDate}.pdf`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
