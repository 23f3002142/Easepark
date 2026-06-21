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

export async function login(data: {
  username: string
  password: string
}): Promise<{ token: string; refresh_token: string; user: User }> {
  const res = await api.post('/auth/login', data)
  return res.data
}

// ── Pre-registration email verification ────────────────────────────────────
// Sends an OTP to the email before account creation

export async function sendVerificationOtp(data: {
  email: string
}): Promise<{ message: string }> {
  const res = await api.post('/auth/send-verification-otp', data)
  return res.data
}

export async function verifyRegistrationOtp(data: {
  email: string
  otp: string
}): Promise<{ message: string }> {
  const res = await api.post('/auth/verify-registration-otp', data)
  return res.data
}

export async function register(data: {
  username: string
  email: string
  password: string
  email_otp: string
}): Promise<{ message: string }> {
  const res = await api.post('/auth/register', data)
  return res.data
}

// ── Email verification for existing users (profile page) ───────────────────

export async function verifyEmail(data: {
  email: string
  otp: string
}): Promise<{ message: string }> {
  const res = await api.post('/auth/verify-email', data)
  return res.data
}

export async function resendVerification(data: {
  email: string
}): Promise<{ message: string }> {
  const res = await api.post('/auth/resend-verification', data)
  return res.data
}

// ── Forgot / Reset password ────────────────────────────────────────────────

export async function forgotPassword(data: {
  email: string
}): Promise<{ message: string }> {
  const res = await api.post('/auth/forgot-password', data)
  return res.data
}

export async function resetPassword(data: {
  email: string
  otp: string
  new_password: string
}): Promise<{ message: string }> {
  const res = await api.post('/auth/reset-password', data)
  return res.data
}

// ── Token refresh & logout ─────────────────────────────────────────────────

export async function refreshAccessToken(refreshToken: string): Promise<{ token: string }> {
  const res = await api.post(
    '/auth/refresh',
    {},
    { headers: { Authorization: `Bearer ${refreshToken}` } }
  )
  return res.data
}

export async function logoutApi(): Promise<void> {
  await api.post('/auth/logout')
}

// ── Profile ────────────────────────────────────────────────────────────────

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
