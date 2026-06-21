import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/user'
import * as authApi from '@/api/auth.api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isUser = computed(() => user.value?.role === 'user')

  async function login(username: string, password: string) {
    const res = await authApi.login({ username, password })
    token.value = res.token
    refreshToken.value = res.refresh_token
    user.value = res.user
    localStorage.setItem('token', res.token)
    localStorage.setItem('refresh_token', res.refresh_token)
  }

  async function register(data: { username: string; email: string; password: string; email_otp: string }) {
    return await authApi.register(data)
  }

  async function fetchProfile() {
    if (!token.value) return
    try {
      user.value = await authApi.getProfile()
    } catch {
      logout()
    }
  }

  function setToken(newToken: string, newRefreshToken?: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
    if (newRefreshToken) {
      refreshToken.value = newRefreshToken
      localStorage.setItem('refresh_token', newRefreshToken)
    }
  }

  async function logout() {
    try {
      if (token.value) await authApi.logoutApi()
    } catch {
      // Logout API call failing is OK — clear local state anyway
    }
    token.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
  }

  return {
    user, token, refreshToken,
    isAuthenticated, isAdmin, isUser,
    login, register, fetchProfile, setToken, logout,
  }
})
