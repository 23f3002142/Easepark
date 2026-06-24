<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import { getProfile } from '@/api/user.api'
import { resendVerification, verifyEmail } from '@/api/auth.api'
import { useToast } from '@/composables/useToast'
import type { User } from '@/types/user'
import { Settings, Lock, AlertTriangle, CheckCircle, Mail } from 'lucide-vue-next'

const toast = useToast()
const user = ref<User | null>(null)
const loading = ref(true)
const error = ref('')

// ── Email verification state (for unverified users) ────────────────────────
const verifyOtpSent = ref(false)
const verifyOtp = ref('')
const verifyLoading = ref(false)
const verifyError = ref('')
const resendCooldown = ref(0)
let cooldownTimer: ReturnType<typeof setInterval> | null = null

onMounted(async () => {
  try {
    const res = await getProfile()
    user.value = res.user
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load profile'
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})

async function handleSendVerificationOtp() {
  if (!user.value) return
  verifyError.value = ''
  verifyLoading.value = true
  try {
    await resendVerification({ email: user.value.email })
    verifyOtpSent.value = true
    toast.success('Verification OTP sent!')
    startCooldown(60)
  } catch (err: any) {
    verifyError.value = err.response?.data?.error || 'Failed to send OTP'
  } finally {
    verifyLoading.value = false
  }
}

async function handleVerifyEmail() {
  if (!user.value) return
  if (verifyOtp.value.length !== 6) {
    verifyError.value = 'Please enter the full 6-digit OTP'
    return
  }
  verifyError.value = ''
  verifyLoading.value = true
  try {
    await verifyEmail({ email: user.value.email, otp: verifyOtp.value })
    user.value.is_verified = true
    verifyOtpSent.value = false
    toast.success('Email verified successfully!')
  } catch (err: any) {
    verifyError.value = err.response?.data?.error || 'Verification failed'
  } finally {
    verifyLoading.value = false
  }
}

function startCooldown(seconds: number) {
  resendCooldown.value = seconds
  if (cooldownTimer) clearInterval(cooldownTimer)
  cooldownTimer = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0 && cooldownTimer) clearInterval(cooldownTimer)
  }, 1000)
}

const fields = [
  { label: 'Username', key: 'username' },
  { label: 'Full Name', key: 'full_name' },
  { label: 'Email', key: 'email' },
  { label: 'Phone Number', key: 'phone_number' },
  { label: 'Address', key: 'address' },
  { label: 'Pin Code', key: 'pin_code' },
] as const
</script>

<template>
  <DashboardLayout>
    <div v-if="loading" class="flex items-center justify-center py-32">
      <div class="w-8 h-8 border-4 border-black border-t-transparent animate-spin"></div>
    </div>

    <div v-else-if="error" class="py-16 text-center">
      <p class="text-red-600 font-bold text-lg">{{ error }}</p>
    </div>

    <div v-else-if="user" class="max-w-2xl mx-auto">
      <PageHeader title="My Profile" :subtitle="`EasePark member since ${user.member_since ? new Date(user.member_since).toLocaleDateString() : 'N/A'}`" />

      <!-- Email Verification Warning Banner -->
      <div v-if="!user.is_verified" class="mb-6 bg-yellow-50 border-2 border-yellow-500 p-5 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <div class="flex items-start gap-3">
          <AlertTriangle :size="20" class="text-yellow-600 mt-0.5 flex-shrink-0" />
          <div class="flex-1">
            <p class="font-bold text-black text-sm uppercase tracking-wider mb-1">Email Not Verified</p>
            <p class="text-gray-600 text-sm mb-3">
              Verify your email to book parking spots and access all features.
            </p>

            <div v-if="verifyError" class="mb-3 p-2 bg-red-50 border border-red-300 text-red-600 text-xs font-bold">
              {{ verifyError }}
            </div>

            <!-- Send OTP button (initial state) -->
            <div v-if="!verifyOtpSent">
              <button
                @click="handleSendVerificationOtp"
                :disabled="verifyLoading"
                class="px-6 py-2 bg-black text-white text-xs font-bold uppercase tracking-wider hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
              >
                <span v-if="verifyLoading">Sending...</span>
                <span v-else>Send Verification OTP</span>
              </button>
            </div>

            <!-- OTP input (after sending) -->
            <div v-else class="space-y-3">
              <div class="flex gap-2">
                <input
                  v-model="verifyOtp"
                  type="text"
                  inputmode="numeric"
                  maxlength="6"
                  placeholder="Enter 6-digit OTP"
                  autocomplete="one-time-code"
                  class="flex-1 px-4 py-2 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none text-sm font-medium tracking-[0.2em] text-center"
                />
                <button
                  @click="handleVerifyEmail"
                  :disabled="verifyLoading"
                  class="px-5 py-2 bg-black text-white text-xs font-bold uppercase tracking-wider hover:bg-gray-800 disabled:bg-gray-400 transition-colors whitespace-nowrap"
                >
                  <span v-if="verifyLoading">Verifying...</span>
                  <span v-else>Verify</span>
                </button>
              </div>
              <div class="flex justify-between items-center">
                <p class="text-xs text-gray-400 flex items-center gap-1">
                  <Mail :size="12" /> OTP sent to {{ user.email }}
                </p>
                <button
                  @click="handleSendVerificationOtp"
                  :disabled="resendCooldown > 0 || verifyLoading"
                  class="text-xs text-black font-bold uppercase tracking-wider hover:underline disabled:text-gray-300"
                >
                  {{ resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend OTP' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Verified badge -->
      <div v-else class="mb-6 inline-flex items-center gap-2 px-3 py-1.5 bg-green-500 border-2 border-black text-black font-bold uppercase tracking-wider text-xs shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
        <CheckCircle :size="14" class="text-black" />
        <span>Verified User</span>
      </div>

      <div class="bg-white border-2 border-black p-8 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <div class="space-y-6">
          <div v-for="field in fields" :key="field.key" class="flex flex-col sm:flex-row sm:items-center border-b border-gray-200 pb-4 last:border-0 last:pb-0">
            <span class="text-sm font-bold text-gray-500 uppercase tracking-wider w-40 mb-1 sm:mb-0">{{ field.label }}</span>
            <span class="font-bold text-black text-lg break-all">{{ (user as any)[field.key] || 'N/A' }}</span>
          </div>
        </div>

        <div class="mt-8 flex items-center justify-center gap-4 flex-wrap">
          <RouterLink
            to="/profile/edit"
            class="inline-flex items-center gap-2 px-8 py-3 bg-black text-white font-bold uppercase tracking-widest text-sm hover:bg-gray-800 transition-colors"
          >
            <Settings :size="16" /> Edit Profile
          </RouterLink>
          <RouterLink
            to="/change-password"
            class="inline-flex items-center gap-2 px-8 py-3 bg-white text-black border-2 border-black font-bold uppercase tracking-widest text-sm hover:bg-gray-100 transition-colors"
          >
            <Lock :size="16" /> Change Password
          </RouterLink>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>
