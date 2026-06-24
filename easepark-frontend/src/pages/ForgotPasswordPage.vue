<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { forgotPassword, resetPassword } from '@/api/auth.api'
import { CircleParking, Eye, EyeOff } from 'lucide-vue-next'

const router = useRouter()
const toast = useToast()

// Step 1 — send OTP
const email = ref('')
const loading = ref(false)
const error = ref('')
const otpSent = ref(false)

// Step 2 — verify OTP + reset
const otp = ref('')
const newPassword = ref('')
const confirmNewPassword = ref('')
const showPassword = ref(false)
const resetLoading = ref(false)
const resetError = ref('')
const resetFieldErrors = ref<Record<string, string[]>>({})
const fieldErrors = ref<Record<string, string[]>>({})

async function handleSendOTP() {
  error.value = ''
  if (!email.value) {
    error.value = 'Please enter your email address'
    return
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value)) {
    error.value = 'Please enter a valid email address'
    return
  }
  loading.value = true
  fieldErrors.value = {}
  try {
    const res = await forgotPassword({ email: email.value })
    toast.success(res.message)
    otpSent.value = true
  } catch (err: any) {
    if (err.response?.status === 422) {
      fieldErrors.value = err.response.data.errors || {}
      error.value = 'Validation failed. Please correct the highlighted field.'
    } else {
      error.value = err.response?.data?.error || 'Something went wrong. Try again.'
    }
  } finally {
    loading.value = false
  }
}

async function handleReset() {
  resetError.value = ''
  if (!otp.value || !newPassword.value || !confirmNewPassword.value) {
    resetError.value = 'Please fill in all fields'
    return
  }
  if (newPassword.value !== confirmNewPassword.value) {
    resetError.value = 'Passwords do not match'
    return
  }
  if (newPassword.value.length < 6) {
    resetError.value = 'Password must be at least 6 characters'
    return
  }

  resetLoading.value = true
  resetFieldErrors.value = {}
  try {
    await resetPassword({ email: email.value, otp: otp.value, new_password: newPassword.value })
    toast.success('Password reset successfully!')
    setTimeout(() => router.push('/login'), 1200)
  } catch (err: any) {
    if (err.response?.status === 422) {
      resetFieldErrors.value = err.response.data.errors || {}
      resetError.value = 'Validation failed. Please correct the highlighted fields.'
    } else {
      resetError.value = err.response?.data?.error || 'Reset failed. Check the OTP and try again.'
    }
  } finally {
    resetLoading.value = false
  }
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
        <h2 class="text-3xl font-bold text-black text-center mb-2 uppercase tracking-tighter">
          {{ otpSent ? 'Reset Password' : 'Forgot Password?' }}
        </h2>
        <p class="text-gray-500 text-center text-sm mb-8 font-medium">
          {{ otpSent ? 'Enter the OTP sent to your email' : 'Enter your email to receive a reset OTP' }}
        </p>

        <!-- Step 1: Email input -->
        <div v-if="!otpSent">
          <div v-if="error" class="mb-6 p-4 bg-red-50 border-2 border-red-600 text-red-600 text-sm font-bold">
            {{ error }}
          </div>

          <form @submit.prevent="handleSendOTP" class="space-y-5">
            <div>
              <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Email Address</label>
              <input
                v-model="email"
                type="email"
                placeholder="Enter your registered email"
                class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none transition-all text-sm font-medium"
              />
            </div>
            <p v-if="fieldErrors.email" class="mb-4 text-xs text-red-600 font-bold">
              {{ fieldErrors.email.join(', ') }}
            </p>

            <button
              type="submit"
              :disabled="loading"
              class="w-full py-4 bg-black text-white font-bold uppercase tracking-widest hover:bg-gray-800 disabled:bg-gray-400 transition-colors text-sm"
            >
              <span v-if="loading">Sending OTP...</span>
              <span v-else>Send Reset OTP</span>
            </button>
          </form>
        </div>

        <!-- Step 2: OTP + New password -->
        <div v-else>
          <div v-if="resetError" class="mb-6 p-4 bg-red-50 border-2 border-red-600 text-red-600 text-sm font-bold">
            {{ resetError }}
          </div>

          <form @submit.prevent="handleReset" class="space-y-5">
            <div>
              <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">OTP Code</label>
              <input
                v-model="otp"
                type="text"
                inputmode="numeric"
                maxlength="6"
                placeholder="Enter 6-digit OTP"
                autocomplete="one-time-code"
                class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none transition-all text-sm font-medium tracking-[0.3em] text-center"
              />
            </div>
            <p v-if="resetFieldErrors.otp" class="mt-1 text-xs text-red-600 font-bold">
              {{ resetFieldErrors.otp.join(', ') }}
            </p>
            <div>
              <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">New Password</label>
              <div class="relative">
                <input
                  v-model="newPassword"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="At least 6 characters"
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
            <p v-if="resetFieldErrors.new_password" class="mt-1 text-xs text-red-600 font-bold">
              {{ resetFieldErrors.new_password.join(', ') }}
            </p>
            <div>
              <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Confirm Password</label>
              <input
                v-model="confirmNewPassword"
                type="password"
                placeholder="Re-enter new password"
                class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none transition-all text-sm font-medium"
              />
            </div>

            <button
              type="submit"
              :disabled="resetLoading"
              class="w-full py-4 bg-black text-white font-bold uppercase tracking-widest hover:bg-gray-800 disabled:bg-gray-400 transition-colors text-sm"
            >
              <span v-if="resetLoading">Resetting...</span>
              <span v-else>Reset Password</span>
            </button>
          </form>

          <button
            @click="otpSent = false; otp = ''; newPassword = ''; confirmNewPassword = ''; resetError = ''"
            class="w-full mt-4 text-sm text-gray-500 hover:text-black font-bold uppercase tracking-wider text-center"
          >
            ← Use a different email
          </button>
        </div>

        <p class="text-center text-sm text-gray-500 mt-8 font-medium">
          Remembered your password?
          <RouterLink to="/login" class="text-black font-bold hover:underline">Sign In</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
