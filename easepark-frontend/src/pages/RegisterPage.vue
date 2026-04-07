<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { useToast } from '@/composables/useToast'
import { CircleParking, Eye, EyeOff } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''

  if (!username.value || !email.value || !password.value || !confirmPassword.value) {
    error.value = 'Please fill in all fields'
    return
  }
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }
  if (password.value.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }

  loading.value = true
  try {
    await authStore.register({
      username: username.value,
      email: email.value,
      password: password.value,
    })
    toast.success('Account created successfully!')
    router.push({ name: 'login', query: { registered: 'true' } })
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-black flex items-center justify-center px-4 relative overflow-hidden">
    <div class="absolute inset-0 opacity-[0.08]" style="background-image: linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px); background-size: 48px 48px;"></div>

    <div class="relative z-10 w-full max-w-md">
      <div class="text-center mb-10">
        <RouterLink to="/" class="inline-flex items-center gap-3">
          <div class="w-10 h-10 bg-white text-black flex items-center justify-center">
            <CircleParking :size="22" />
          </div>
          <span class="text-white font-bold text-2xl uppercase tracking-widest">EasePark</span>
        </RouterLink>
      </div>

      <div class="bg-white border-2 border-white p-10 shadow-[8px_8px_0px_0px_rgba(255,255,255,0.3)]">
        <h2 class="text-3xl font-bold text-black text-center mb-2 uppercase tracking-tighter">Create Account</h2>
        <p class="text-gray-500 text-center text-sm mb-8 font-medium">Join EasePark today</p>

        <div v-if="error" class="mb-6 p-4 bg-red-50 border-2 border-red-600 text-red-600 text-sm font-bold">
          {{ error }}
        </div>

        <form @submit.prevent="handleRegister" class="space-y-5">
          <div>
            <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Username</label>
            <input
              v-model="username"
              type="text"
              placeholder="Choose a username"
              class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none transition-all text-sm font-medium"
            />
          </div>
          <div>
            <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Email</label>
            <input
              v-model="email"
              type="email"
              placeholder="Enter your email"
              class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none transition-all text-sm font-medium"
            />
          </div>
          <div>
            <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Password</label>
            <div class="relative">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Create a password"
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
          <div>
            <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Confirm Password</label>
            <input
              v-model="confirmPassword"
              type="password"
              placeholder="Confirm your password"
              class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none transition-all text-sm font-medium"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-4 bg-black text-white font-bold uppercase tracking-widest hover:bg-gray-800 disabled:bg-gray-400 transition-colors text-sm"
          >
            <span v-if="loading">Creating account...</span>
            <span v-else>Create Account</span>
          </button>
        </form>

        <p class="text-center text-sm text-gray-500 mt-8 font-medium">
          Already have an account?
          <RouterLink to="/login" class="text-black font-bold hover:underline">Sign In</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
