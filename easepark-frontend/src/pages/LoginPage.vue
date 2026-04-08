<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { useToast } from '@/composables/useToast'
import { getGoogleLoginUrl } from '@/api/auth.api'
import { CircleParking, Eye, EyeOff } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const toast = useToast()

onMounted(() => {
  if (route.query.registered === 'true') {
    toast.success('Registration successful! Please sign in.')
  }

  const oauthError = route.query.oauth_error
  if (typeof oauthError === 'string' && oauthError.trim()) {
    error.value = oauthError
  }
})

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  if (!username.value || !password.value) {
    error.value = 'Please fill in all fields'
    return
  }

  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    toast.success('Logged in successfully!')
    if (authStore.isAdmin) {
      router.push('/admin')
    } else {
      router.push('/dashboard')
    }
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}

function googleLogin() {
  window.location.href = getGoogleLoginUrl()
}
</script>

<template>
  <div class="min-h-screen bg-black flex items-center justify-center px-4 relative overflow-hidden">
    <!-- Grid bg -->
    <div class="absolute inset-0 opacity-[0.08]" style="background-image: linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px); background-size: 48px 48px;"></div>

    <div class="relative z-10 w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-10">
        <RouterLink to="/" class="inline-flex items-center gap-3">
          <div class="w-10 h-10 bg-white text-black flex items-center justify-center">
            <CircleParking :size="22" />
          </div>
          <span class="text-white font-bold text-2xl uppercase tracking-widest">EasePark</span>
        </RouterLink>
      </div>

      <!-- Card -->
      <div class="bg-white border-2 border-white p-10 shadow-[8px_8px_0px_0px_rgba(255,255,255,0.3)]">
        <h2 class="text-3xl font-bold text-black text-center mb-2 uppercase tracking-tighter">Welcome Back</h2>
        <p class="text-gray-500 text-center text-sm mb-8 font-medium">Sign in to your account</p>

        <!-- Error -->
        <div v-if="error" class="mb-6 p-4 bg-red-50 border-2 border-red-600 text-red-600 text-sm font-bold">
          {{ error }}
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Username</label>
            <input
              v-model="username"
              type="text"
              placeholder="Enter your username"
              class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none transition-all text-sm font-medium"
            />
          </div>
          <div>
            <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Password</label>
            <div class="relative">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Enter your password"
                class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none transition-all text-sm font-medium pr-12"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-black"
                @click="showPassword = !showPassword"
              >
                <EyeOff v-if="showPassword" :size="18" />
                <Eye v-else :size="18" />
              </button>
            </div>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-4 bg-black text-white font-bold uppercase tracking-widest hover:bg-gray-800 disabled:bg-gray-400 transition-colors text-sm"
          >
            <span v-if="loading">Signing in...</span>
            <span v-else>Sign In</span>
          </button>
        </form>

        <!-- Divider -->
        <div class="flex items-center gap-4 my-8">
          <div class="flex-1 h-px bg-black"></div>
          <span class="text-xs text-gray-500 font-bold uppercase tracking-widest">Or</span>
          <div class="flex-1 h-px bg-black"></div>
        </div>

        <!-- Google Login -->
        <button
          @click="googleLogin"
          class="w-full flex items-center justify-center gap-3 py-3 bg-white border-2 border-black hover:bg-gray-100 text-black font-bold transition-colors text-sm uppercase tracking-wider"
        >
          <svg class="w-5 h-5" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Google
        </button>

        <p class="text-center text-sm text-gray-500 mt-8 font-medium">
          Don't have an account?
          <RouterLink to="/register" class="text-black font-bold hover:underline">Register</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
