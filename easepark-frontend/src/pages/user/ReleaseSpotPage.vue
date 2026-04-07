<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import {
  getReleaseInfo, releaseSpot, releaseSpotFree, verifyPayment, cancelRelease,
  sendReleaseOtp, verifyReleaseOtp, verifyReleasePassword,
  type ReleaseInfo,
} from '@/api/user.api'
import { ShieldCheck, Lock, Mail, Eye, EyeOff, CreditCard, CheckCircle } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const info = ref<ReleaseInfo | null>(null)
const loading = ref(true)
const error = ref('')
const success = ref('')

// Steps: 'info' → 'choose' → 'otp' | 'password' → 'pay_method' → 'payment'
const step = ref<'info' | 'choose' | 'otp' | 'password' | 'pay_method' | 'payment'>('info')
const releasing = ref(false)
const verifying = ref(false)

// OTP state
const otp = ref('')
const countdown = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

// Password state
const password = ref('')
const showPassword = ref(false)

const reservationId = Number(route.params.id)

onMounted(async () => {
  try {
    info.value = await getReleaseInfo(reservationId)
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load release info'
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', hour12: true
  })
}

function startCountdown() {
  countdown.value = 60
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    if (countdown.value > 0) countdown.value--
    else if (timer) clearInterval(timer)
  }, 1000)
}

function proceedToConfirm() {
  error.value = ''
  step.value = 'choose'
}

async function chooseOtp() {
  error.value = ''
  verifying.value = true
  try {
    await sendReleaseOtp(reservationId)
    step.value = 'otp'
    otp.value = ''
    startCountdown()
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to send OTP'
  } finally {
    verifying.value = false
  }
}

function choosePassword() {
  error.value = ''
  password.value = ''
  step.value = 'password'
}

async function handleVerifyOtp() {
  if (!otp.value.trim() || otp.value.length !== 6) {
    error.value = 'Please enter a valid 6-digit OTP'
    return
  }
  verifying.value = true
  error.value = ''
  try {
    await verifyReleaseOtp(reservationId, otp.value.trim())
    step.value = 'pay_method'
  } catch (err: any) {
    error.value = err.response?.data?.error || 'OTP verification failed'
  } finally {
    verifying.value = false
  }
}

async function handleVerifyPassword() {
  if (!password.value) {
    error.value = 'Password is required'
    return
  }
  verifying.value = true
  error.value = ''
  try {
    await verifyReleasePassword(reservationId, password.value)
    step.value = 'pay_method'
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Password verification failed'
  } finally {
    verifying.value = false
  }
}

function chooseRazorpay() {
  error.value = ''
  step.value = 'payment'
  handlePayment()
}

async function handleReleaseFree() {
  releasing.value = true
  error.value = ''
  try {
    const res = await releaseSpotFree(reservationId)
    success.value = `Spot released! Total cost: ₹${res.total_cost} (${res.duration_hours}h). Payment pending offline.`
    setTimeout(() => router.push('/dashboard'), 2500)
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to release spot'
    releasing.value = false
  }
}

async function handleCancel() {
  try {
    await cancelRelease(reservationId)
  } catch { /* ignore */ }
  router.push('/bookings')
}

async function handlePayment() {
  releasing.value = true
  error.value = ''
  try {
    const paymentData = await releaseSpot(reservationId)

    const options = {
      key: paymentData.razorpay_key_id,
      amount: String(paymentData.amount_paise),
      currency: 'INR',
      name: 'EasePark',
      description: 'Parking Payment',
      order_id: paymentData.order_id,
      handler: async function (response: any) {
        try {
          await verifyPayment({
            payment_id: response.razorpay_payment_id,
            order_id: paymentData.order_id,
            signature: response.razorpay_signature,
            reservation_id: paymentData.reservation_id,
          })
          success.value = 'Payment successful! Spot released.'
          setTimeout(() => router.push('/dashboard'), 2000)
        } catch (err: any) {
          error.value = err.response?.data?.error || 'Payment verification failed'
          releasing.value = false
        }
      },
      prefill: {
        name: paymentData.user_name,
        email: paymentData.user_email,
        contact: paymentData.user_phone,
      },
      theme: { color: '#000000' },
      modal: {
        ondismiss: async function () {
          // Revert pending_release → active so user can try again later
          try { await cancelRelease(reservationId) } catch { /* ignore */ }
          releasing.value = false
          router.push('/bookings')
        }
      }
    }

    const rzp = new (window as any).Razorpay(options)
    rzp.on('payment.failed', async function () {
      // Revert pending_release → active on failure too
      try { await cancelRelease(reservationId) } catch { /* ignore */ }
      releasing.value = false
      error.value = 'Payment failed. Your booking is still active.'
      step.value = 'info'
    })
    rzp.open()
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to initiate release'
    releasing.value = false
  }
}

async function resendOtp() {
  error.value = ''
  verifying.value = true
  try {
    // Cancel current pending_release and re-send
    await cancelRelease(reservationId).catch(() => {})
    await sendReleaseOtp(reservationId)
    otp.value = ''
    startCountdown()
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to resend OTP'
  } finally {
    verifying.value = false
  }
}
</script>

<template>
  <DashboardLayout>
    <div v-if="loading" class="flex items-center justify-center py-32">
      <div class="w-8 h-8 border-4 border-black border-t-transparent animate-spin"></div>
    </div>

    <div v-else-if="error && !info" class="py-16 text-center">
      <p class="text-red-600 font-bold text-lg">{{ error }}</p>
      <button @click="router.push('/bookings')" class="mt-4 px-6 py-3 bg-black text-white font-bold uppercase tracking-wider text-sm">Back to Bookings</button>
    </div>

    <div v-else-if="info" class="max-w-lg mx-auto">
      <div class="text-center mb-8">
        <h1 class="text-3xl md:text-4xl font-bold tracking-tighter text-black">Release Parking Spot</h1>
        <p class="text-lg text-gray-500 font-medium mt-2">
          {{ step === 'info' ? 'Review details and confirm release' : step === 'choose' ? 'Choose confirmation method' : step === 'otp' ? 'Enter OTP to confirm' : step === 'password' ? 'Enter password to confirm' : step === 'pay_method' ? 'Choose payment method' : 'Processing payment...' }}
        </p>
      </div>

      <div class="bg-white border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-8">
        <div v-if="error" class="mb-6 p-4 bg-red-50 border-2 border-red-600 text-red-600 text-sm font-bold">{{ error }}</div>
        <div v-if="success" class="mb-6 p-4 bg-green-50 border-2 border-green-600 text-green-600 text-sm font-bold">{{ success }}</div>

        <!-- Step: Info -->
        <template v-if="step === 'info' && !success">
          <div class="space-y-4">
            <div class="flex justify-between items-center py-3 border-b border-gray-200">
              <span class="text-sm font-bold text-gray-500 uppercase tracking-wider">Spot Number</span>
              <span class="font-bold text-black text-lg">{{ info.spot_number }}</span>
            </div>
            <div class="flex justify-between items-center py-3 border-b border-gray-200">
              <span class="text-sm font-bold text-gray-500 uppercase tracking-wider">Vehicle Number</span>
              <span class="font-bold text-black font-mono">{{ info.vehicle_number }}</span>
            </div>
            <div class="flex justify-between items-center py-3 border-b border-gray-200">
              <span class="text-sm font-bold text-gray-500 uppercase tracking-wider">Parking Time</span>
              <span class="font-bold text-black text-sm">{{ formatDate(info.booking_time) }}</span>
            </div>
            <div class="flex justify-between items-center py-3 border-b border-gray-200">
              <span class="text-sm font-bold text-gray-500 uppercase tracking-wider">Release Time</span>
              <span class="font-bold text-black text-sm">{{ formatDate(info.current_time) }}</span>
            </div>
            <div class="flex justify-between items-center py-3 border-b border-gray-200">
              <span class="text-sm font-bold text-gray-500 uppercase tracking-wider">Cost / Hour</span>
              <span class="font-bold text-black">&#8377;{{ info.cost_per_hour }}</span>
            </div>
            <div class="flex justify-between items-center py-4 bg-gray-50 px-4 -mx-4 border-2 border-black mt-4">
              <span class="text-lg font-bold text-black uppercase tracking-wider">Estimated Cost</span>
              <span class="text-3xl font-bold text-black">&#8377;{{ info.estimated_cost.toFixed(2) }}</span>
            </div>
          </div>
          <div class="flex gap-4 mt-8">
            <button @click="proceedToConfirm" class="flex-1 py-4 bg-black text-white font-bold uppercase tracking-widest text-sm hover:bg-gray-800 transition-colors">
              Proceed to Release
            </button>
            <button @click="router.push('/bookings')" class="flex-1 py-4 bg-white text-black border-2 border-black font-bold uppercase tracking-widest text-sm hover:bg-gray-100 transition-colors">
              Back
            </button>
          </div>
        </template>

        <!-- Step: Choose method -->
        <template v-if="step === 'choose' && !success">
          <p class="text-gray-600 text-sm text-center mb-6">Choose how you'd like to confirm your identity before releasing this spot.</p>
          <div class="space-y-4">
            <button @click="chooseOtp" :disabled="verifying" class="w-full py-4 bg-black text-white font-bold uppercase tracking-widest text-sm hover:bg-gray-800 disabled:bg-gray-400 transition-colors flex items-center justify-center gap-3">
              <Mail :size="18" /> Confirm via OTP (Email)
            </button>
            <button @click="choosePassword" :disabled="verifying" class="w-full py-4 bg-white text-black border-2 border-black font-bold uppercase tracking-widest text-sm hover:bg-gray-100 disabled:opacity-50 transition-colors flex items-center justify-center gap-3">
              <Lock :size="18" /> Confirm via Password
            </button>
          </div>
          <button @click="step = 'info'" class="w-full mt-4 py-3 text-gray-500 text-sm font-bold hover:text-black transition-colors">
            &larr; Back to Details
          </button>
        </template>

        <!-- Step: OTP -->
        <template v-if="step === 'otp' && !success">
          <div class="text-center mb-6">
            <ShieldCheck :size="32" class="mx-auto mb-2 text-black" />
            <p class="text-gray-500 text-sm font-medium">We've sent a 6-digit OTP to your registered email.</p>
          </div>
          <form @submit.prevent="handleVerifyOtp">
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
            <button type="submit" :disabled="verifying" class="w-full py-4 bg-black text-white font-bold uppercase tracking-widest text-sm hover:bg-gray-800 disabled:bg-gray-400 transition-colors">
              {{ verifying ? 'Verifying...' : 'Verify & Pay' }}
            </button>
          </form>
          <div class="mt-4 text-center text-sm text-gray-500">
            Didn't receive?
            <span v-if="countdown > 0" class="font-bold text-red-600">{{ countdown }}s</span>
            <button v-else @click="resendOtp" class="font-bold text-black hover:underline">Resend</button>
          </div>
          <button @click="handleCancel" class="w-full mt-4 py-3 bg-white text-red-600 border-2 border-red-600 font-bold uppercase tracking-widest text-sm hover:bg-red-50 transition-colors">
            Cancel Release
          </button>
        </template>

        <!-- Step: Password -->
        <template v-if="step === 'password' && !success">
          <div class="text-center mb-6">
            <Lock :size="32" class="mx-auto mb-2 text-black" />
            <p class="text-gray-500 text-sm font-medium">Enter your account password to confirm.</p>
          </div>
          <form @submit.prevent="handleVerifyPassword">
            <div class="mb-6">
              <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Password</label>
              <div class="relative">
                <input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Enter your password"
                  class="w-full px-4 py-4 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none pr-12"
                />
                <button type="button" @click="showPassword = !showPassword" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-black">
                  <Eye v-if="!showPassword" :size="20" />
                  <EyeOff v-else :size="20" />
                </button>
              </div>
            </div>
            <button type="submit" :disabled="verifying" class="w-full py-4 bg-black text-white font-bold uppercase tracking-widest text-sm hover:bg-gray-800 disabled:bg-gray-400 transition-colors">
              {{ verifying ? 'Verifying...' : 'Verify & Pay' }}
            </button>
          </form>
          <button @click="step = 'choose'" class="w-full mt-4 py-3 text-gray-500 text-sm font-bold hover:text-black transition-colors">
            &larr; Back to Options
          </button>
        </template>

        <!-- Step: Choose payment method -->
        <template v-if="step === 'pay_method' && !success">
          <div class="text-center mb-6">
            <CheckCircle :size="32" class="mx-auto mb-2 text-green-600" />
            <p class="text-green-600 text-sm font-bold mb-1">Identity Verified!</p>
            <p class="text-gray-500 text-sm font-medium">Choose how you'd like to complete the release.</p>
          </div>

          <div v-if="info" class="mb-6 p-4 bg-gray-50 border-2 border-gray-200">
            <div class="flex justify-between items-center">
              <span class="text-sm font-bold text-gray-500 uppercase tracking-wider">Estimated Cost</span>
              <span class="text-2xl font-bold text-black">&#8377;{{ info.estimated_cost.toFixed(2) }}</span>
            </div>
          </div>

          <div class="space-y-4">
            <button
              @click="chooseRazorpay"
              :disabled="releasing"
              class="w-full py-4 bg-black text-white font-bold uppercase tracking-widest text-sm hover:bg-gray-800 disabled:bg-gray-400 transition-colors flex items-center justify-center gap-3"
            >
              <CreditCard :size="18" /> Pay via Razorpay
            </button>
            <div class="relative">
              <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-gray-300"></div></div>
              <div class="relative flex justify-center"><span class="bg-white px-4 text-xs font-bold text-gray-400 uppercase tracking-wider">or</span></div>
            </div>
            <button
              @click="handleReleaseFree"
              :disabled="releasing"
              class="w-full py-4 bg-white text-black border-2 border-black font-bold uppercase tracking-widest text-sm hover:bg-gray-100 disabled:opacity-50 transition-colors flex items-center justify-center gap-3"
            >
              <Lock :size="18" /> Confirm &amp; Release (Skip Payment)
            </button>
            <p class="text-center text-xs text-gray-400">Razorpay is in beta. Choose "Skip Payment" to release without online payment.</p>
          </div>

          <button @click="handleCancel" class="w-full mt-4 py-3 bg-white text-red-600 border-2 border-red-600 font-bold uppercase tracking-widest text-sm hover:bg-red-50 transition-colors">
            Cancel Release
          </button>
        </template>

        <!-- Step: Payment processing (shown briefly) -->
        <template v-if="step === 'payment' && !success">
          <div class="py-8 text-center">
            <div class="w-10 h-10 border-4 border-black border-t-transparent animate-spin mx-auto mb-4"></div>
            <p class="font-bold text-black uppercase tracking-wider">Initiating Payment...</p>
          </div>
        </template>
      </div>
    </div>
  </DashboardLayout>
</template>
