import api from './axios'
import type { ParkingLot } from '@/types/parking'
import type { User } from '@/types/user'

export interface AdminLot {
  id: number
  parking_name: string
  price: number
  address: string
  pin_code: string
  max_spots: number
  latitude: number | null
  longitude: number | null
  total_spots: number
  occupied_spots: number
  available_spots: number
}

export interface AdminLotDetail {
  id: number
  parking_name: string
  price: number
  address: string
  pin_code: string
  max_spots: number
  latitude: number | null
  longitude: number | null
  is_active: boolean
  spots: Array<{
    id: number
    spot_number: string
    status: 'A' | 'O'
    is_active: boolean
  }>
}

export interface AdminSummary {
  total_spots: number
  occupied_spots: number
  available_spots: number
  months: string[]
  bookings_per_month: number[]
  registration_labels: string[]
  registration_data: number[]
  top_lot_labels: string[]
  top_lot_data: number[]
  avg_time_labels: string[]
  avg_time_data: number[]
}

export interface UserHistory {
  user: User
  history: Array<{
    id: number
    lot_name: string
    spot_number: string
    vehicle_number: string
    booking_timestamp: string
    releasing_timestamp: string | null
    total_cost: number | null
    status: string
  }>
  total_amount_paid: number
  total_duration_hours: number
  total_bookings: number
  first_booking: string | null
  latest_booking: string | null
}

export async function getDashboard(): Promise<{ lots: AdminLot[] }> {
  const { data } = await api.get('/admin/dashboard')
  return data
}

export async function getProfile(): Promise<{ user: User }> {
  const { data } = await api.get('/admin/profile')
  return data
}

export async function updateProfile(payload: Partial<User>): Promise<{ message: string; user: User }> {
  const { data } = await api.put('/admin/profile', payload)
  return data
}

export async function addLot(payload: {
  parking_name: string
  price: number
  address: string
  pin_code: string
  max_spots: number
  latitude?: number | null
  longitude?: number | null
}): Promise<{ message: string; lot_id: number }> {
  const { data } = await api.post('/admin/lots', payload)
  return data
}

export async function getLot(lotId: number): Promise<{ lot: AdminLotDetail }> {
  const { data } = await api.get(`/admin/lots/${lotId}`)
  return data
}

export async function editLot(lotId: number, payload: {
  parking_name?: string
  price?: number
  address?: string
  pin_code?: string
  max_spots?: number
  latitude?: number | null
  longitude?: number | null
}): Promise<{ message: string }> {
  const { data } = await api.put(`/admin/lots/${lotId}`, payload)
  return data
}

export async function deleteLot(lotId: number): Promise<{ message: string }> {
  const { data } = await api.delete(`/admin/lots/${lotId}`)
  return data
}

export async function getSpot(spotId: number): Promise<{ spot: any }> {
  const { data } = await api.get(`/admin/spots/${spotId}`)
  return data
}

export async function deleteSpot(spotId: number): Promise<{ message: string }> {
  const { data } = await api.delete(`/admin/spots/${spotId}`)
  return data
}

export async function getUsers(): Promise<{ users: User[] }> {
  const { data } = await api.get('/admin/users')
  return data
}

export async function getUserHistory(userId: number): Promise<UserHistory> {
  const { data } = await api.get(`/admin/users/${userId}/history`)
  return data
}

export async function getSummary(): Promise<AdminSummary> {
  const { data } = await api.get('/admin/summary')
  return data
}

export async function adminSearch(type: string, q: string): Promise<{ results: any[]; search_type: string; query: string }> {
  const { data } = await api.get('/admin/search', { params: { type, q } })
  return data
}
