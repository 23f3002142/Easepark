import api from './axios'
import type { User } from '@/types/user'

function normalizedApiBaseUrl(): string {
  const raw = String(import.meta.env.VITE_API_URL || '/api').trim()
  if (!raw) return '/api'
  return raw.replace(/\/+$/, '')
}

export function getGoogleLoginUrl(): string {
  return `${normalizedApiBaseUrl()}/auth/google-login`
}

export async function login(data: { username: string; password: string }): Promise<{ token: string; user: User }> {
  const res = await api.post('/auth/login', data)
  return res.data
}

export async function register(data: { username: string; email: string; password: string }): Promise<void> {
  await api.post('/auth/register', data)
}

export async function getProfile(): Promise<User> {
  const res = await api.get('/auth/me')
  return res.data.user
}

export async function changePassword(data: {
  current_password: string
  new_password: string
  confirm_password: string
}): Promise<{ message: string }> {
  const res = await api.post('/auth/change-password', data)
  return res.data
}
