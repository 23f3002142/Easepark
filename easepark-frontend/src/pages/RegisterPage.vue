<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { useToast } from '@/composables/useToast'
import { getGoogleLoginUrl, sendVerificationOtp, verifyRegistrationOtp } from '@/api/auth.api'
import { CircleParking, Eye, EyeOff, CheckCircle, Mail } from 'lucide-vue-next'

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

// ── Inline email verification state ────────────────────────────────────────
const emailVerified = ref(false)
const verifyLoading = ref(false)
const verifyError = ref('')
const otpSent = ref(false)
const otpCode = ref('')
const otpVerifying = ref(false)
const resendCooldown = ref(0)
const fieldErrors = ref<Record<string, string[]>>({})

let cooldownTimer: ReturnType<typeof setInterval> | null = null

// Store the verified OTP so we can send it with the register request
const verifiedOtp = ref('')

const canCreateAccount = computed(() =>
  username.value &&
  email.value &&
  password.value &&
  confirmPassword.value &&
  emailVerified.value
)

// ── Send verification OTP to the email ─────────────────────────────────────
async function handleSendOtp() {
  if (!email.value) {
    verifyError.value = 'Please enter your email first'
    return
  }
  verifyError.value = ''
  verifyLoading.value = true
  try {
    await sendVerificationOtp({ email: email.value })
    otpSent.value = true
    toast.success('Verification OTP sent to your email!')
    startCooldown(60)
  } catch (err: any) {
    if (err.response?.status === 422 && err.response?.data?.errors?.email) {
      verifyError.value = err.response.data.errors.email.join(', ')
    } else {
      verifyError.value = err.response?.data?.error || 'Failed to send OTP'
    }
  } finally {
    verifyLoading.value = false
  }
}

// ── Verify the OTP (checked server-side inline) ───────────────────
async function handleVerifyOtp() {
  if (otpCode.value.length !== 6) {
    verifyError.value = 'Please enter the full 6-digit OTP'
    return
  }
  verifyError.value = ''
  otpVerifying.value = true
  try {
    await verifyRegistrationOtp({
      email: email.value,
      otp: otpCode.value,
    })
    verifiedOtp.value = otpCode.value
    emailVerified.value = true
    toast.success('Email verified successfully!')
  } catch (err: any) {
    if (err.response?.status === 422) {
      const errors = err.response.data.errors || {}
      const msg = errors.otp?.join(', ') || errors.email?.join(', ')
      verifyError.value = msg || 'Verification failed. Please try again.'
    } else {
      verifyError.value = err.response?.data?.error || 'Verification failed. Please try again.'
    }
  } finally {
    otpVerifying.value = false
  }
}

function startCooldown(seconds: number) {
  resendCooldown.value = seconds
  if (cooldownTimer) clearInterval(cooldownTimer)
  cooldownTimer = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0 && cooldownTimer) {
      clearInterval(cooldownTimer)
    }
  }, 1000)
}

onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})

// ── Handle registration ────────────────────────────────────────────────────
async function handleRegister() {
  error.value = ''
  fieldErrors.value = {}

  if (!username.value || !email.value || !password.value || !confirmPassword.value) {
    error.value = 'Please fill in all fields'
    return
  }
  if (!emailVerified.value) {
    error.value = 'Please verify your email first'
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
      email_otp: '', // Checked server-side via email_verified status in Redis
    })
    toast.success('Account created successfully!')
    router.push({ name: 'login', query: { registered: 'true' } })
  } catch (err: any) {
    if (err.response?.status === 422) {
      fieldErrors.value = err.response.data.errors || {}
      error.value = 'Validation failed. Please correct the highlighted fields.'
    } else {
      error.value = err.response?.data?.error || 'Registration failed. Please try again.'
    }
    // If OTP was invalid, reset verification state so they can retry
    if (err.response?.data?.error?.includes('OTP')) {
      emailVerified.value = false
      verifiedOtp.value = ''
      otpCode.value = ''
    }
  } finally {
    loading.value = false
  }
}

function googleSignup() {
  window.location.href = getGoogleLoginUrl()
}
</script>

<template>
  <div class="min-h-screen bg-black flex items-center justify-center px-4 relative overflow-hidden">
    <!-- Grid bg -->
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
          <!-- Username -->
          <div>
            <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Username</label>
            <input
              v-model="username"
              type="text"
              placeholder="Choose a username"
              class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none transition-all text-sm font-medium"
            />
            <p v-if="fieldErrors.username" class="mt-1 text-xs text-red-600 font-bold">
              {{ fieldErrors.username.join(', ') }}
            </p>
          </div>

          <!-- Email + inline verification -->
          <div>
            <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Email</label>
            <div class="flex gap-2">
              <input
                v-model="email"
                type="email"
                placeholder="Enter your email"
                :disabled="emailVerified"
                class="flex-1 px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none transition-all text-sm font-medium disabled:bg-gray-100 disabled:text-gray-500"
              />
              <!-- Verify button / Verified badge -->
              <button
                v-if="!emailVerified && !otpSent"
                type="button"
                :disabled="verifyLoading || !email"
                @click="handleSendOtp"
                class="px-4 py-3 bg-black text-white text-xs font-bold uppercase tracking-wider hover:bg-gray-800 disabled:bg-gray-400 transition-colors whitespace-nowrap"
              >
                <span v-if="verifyLoading">Sending...</span>
                <span v-else>Verify</span>
              </button>
              <div v-if="emailVerified" class="flex items-center px-3 bg-green-50 border-2 border-green-600">
                <CheckCircle :size="18" class="text-green-600" />
              </div>
            </div>
            <p v-if="fieldErrors.email" class="mt-1 text-xs text-red-600 font-bold">
              {{ fieldErrors.email.join(', ') }}
            </p>

            <!-- OTP input row (appears after Send OTP) -->
            <div v-if="otpSent && !emailVerified" class="mt-3 space-y-2">
              <div v-if="verifyError" class="p-2 bg-red-50 border border-red-300 text-red-600 text-xs font-bold">
                {{ verifyError }}
              </div>
              <div class="flex gap-2">
                <input
                  v-model="otpCode"
                  type="text"
                  inputmode="numeric"
                  maxlength="6"
                  placeholder="Enter 6-digit OTP"
                  autocomplete="one-time-code"
                  class="flex-1 px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none transition-all text-sm font-medium tracking-[0.2em] text-center"
                />
                <button
                  type="button"
                  :disabled="otpVerifying"
                  @click="handleVerifyOtp"
                  class="px-4 py-3 bg-black text-white text-xs font-bold uppercase tracking-wider hover:bg-gray-800 disabled:bg-gray-400 transition-colors whitespace-nowrap"
                >
                  <span v-if="otpVerifying">Verifying...</span>
                  <span v-else>Confirm</span>
                </button>
              </div>
              <div class="flex justify-between items-center">
                <p class="text-xs text-gray-400 flex items-center gap-1">
                  <Mail :size="12" /> Check your inbox
                </p>
                <button
                  type="button"
                  :disabled="resendCooldown > 0 || verifyLoading"
                  @click="handleSendOtp"
                  class="text-xs text-black font-bold uppercase tracking-wider hover:underline disabled:text-gray-300 disabled:no-underline"
                >
                  {{ resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend OTP' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Password -->
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
            <p v-if="fieldErrors.password" class="mt-1 text-xs text-red-600 font-bold">
              {{ fieldErrors.password.join(', ') }}
            </p>
          </div>

          <!-- Confirm password -->
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
            :disabled="loading || !canCreateAccount"
            class="w-full py-4 bg-black text-white font-bold uppercase tracking-widest hover:bg-gray-800 disabled:bg-gray-400 transition-colors text-sm"
          >
            <span v-if="loading">Creating account...</span>
            <span v-else>Create Account</span>
          </button>
        </form>

        <div class="flex items-center gap-4 my-8">
          <div class="flex-1 h-px bg-black"></div>
          <span class="text-xs text-gray-500 font-bold uppercase tracking-widest">Or</span>
          <div class="flex-1 h-px bg-black"></div>
        </div>

        <button
          @click="googleSignup"
          class="w-full flex items-center justify-center gap-3 py-3 bg-white border-2 border-black hover:bg-gray-100 text-black font-bold transition-colors text-sm uppercase tracking-wider"
        >
          <svg class="w-5 h-5" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continue with Google
        </button>

        <p class="text-center text-sm text-gray-500 mt-8 font-medium">
          Already have an account?
          <RouterLink to="/login" class="text-black font-bold hover:underline">Sign In</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
