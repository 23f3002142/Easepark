<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { verifyReleaseOtp } from '@/api/user.api'
import { ShieldCheck } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const reservationId = ref(0)
const otp = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')
const countdown = ref(60)
let timer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  const id = route.query.reservation_id
  if (!id) {
    router.push('/book')
    return
  }
  reservationId.value = Number(id)
  startTimer()
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

function startTimer() {
  countdown.value = 60
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      if (timer) clearInterval(timer)
    }
  }, 1000)
}

async function handleVerify() {
  if (!otp.value.trim() || otp.value.length !== 6) {
    error.value = 'Please enter a valid 6-digit OTP'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await verifyReleaseOtp(reservationId.value, otp.value.trim())
    success.value = res.message
    setTimeout(() => router.push('/bookings'), 1500)
  } catch (err: any) {
    error.value = err.response?.data?.error || 'OTP verification failed'
  } finally {
    loading.value = false
  }
}

function resend() {
  window.location.reload()
}
</script>

<template>
  <DashboardLayout>
    <div class="flex items-center justify-center min-h-[70vh]">
      <div class="w-full max-w-md">
        <div class="bg-white border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
          <!-- Header -->
          <div class="bg-black text-white p-6 text-center">
            <ShieldCheck :size="32" class="mx-auto mb-2" />
            <h2 class="text-xl font-bold uppercase tracking-widest">OTP Verification</h2>
          </div>

          <!-- Body -->
          <div class="p-8">
            <p class="text-gray-500 text-sm text-center mb-6 font-medium">
              We've sent a 6-digit OTP to your registered email. Please enter it below.
            </p>

            <div v-if="error" class="mb-4 p-3 bg-red-50 border-2 border-red-600 text-red-600 text-sm font-bold">{{ error }}</div>
            <div v-if="success" class="mb-4 p-3 bg-green-50 border-2 border-green-600 text-green-600 text-sm font-bold">{{ success }}</div>

            <form @submit.prevent="handleVerify">
              <div class="mb-6">
                <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Enter OTP</label>
                <input
                  v-model="otp"
                  type="text"
                  maxlength="6"
                  minlength="6"
                  placeholder="------"
                  class="w-full px-4 py-4 border-2 border-black text-center text-2xl font-bold tracking-[0.5em] focus:ring-0 focus:border-gray-600 outline-none"
                />
              </div>

              <button
                type="submit"
                :disabled="loading"
                class="w-full py-4 bg-black text-white font-bold uppercase tracking-widest text-sm hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
              >
                {{ loading ? 'Verifying...' : 'Verify & Confirm' }}
              </button>
            </form>
          </div>

          <!-- Footer -->
          <div class="border-t-2 border-gray-200 px-8 py-4 text-center bg-gray-50">
            <p class="text-sm text-gray-500">
              Didn't receive the OTP?
              <span v-if="countdown > 0" class="font-bold text-red-600">{{ countdown }}s</span>
              <button v-else @click="resend" class="font-bold text-black hover:underline">Resend</button>
            </p>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>
