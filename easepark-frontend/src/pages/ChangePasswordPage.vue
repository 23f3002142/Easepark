<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { changePassword } from '@/api/auth.api'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth.store'
import { Lock, Eye, EyeOff, ArrowLeft } from 'lucide-vue-next'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()

const form = ref({
  current_password: '',
  new_password: '',
  confirm_password: '',
})
const loading = ref(false)
const error = ref('')
const showCurrent = ref(false)
const showNew = ref(false)
const showConfirm = ref(false)

async function handleSubmit() {
  error.value = ''

  if (!form.value.current_password || !form.value.new_password || !form.value.confirm_password) {
    error.value = 'All fields are required'
    return
  }

  if (form.value.new_password.length < 6) {
    error.value = 'New password must be at least 6 characters'
    return
  }

  if (form.value.new_password !== form.value.confirm_password) {
    error.value = 'New passwords do not match'
    return
  }

  loading.value = true
  try {
    const res = await changePassword(form.value)
    toast.success(res.message)
    form.value = { current_password: '', new_password: '', confirm_password: '' }
    const target = authStore.isAdmin ? '/admin/profile' : '/profile'
    setTimeout(() => router.push(target), 1500)
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to change password'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <DashboardLayout>
    <div class="flex items-center justify-center min-h-[70vh]">
      <div class="w-full max-w-md">
        <div class="bg-white border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
          <!-- Header -->
          <div class="bg-black text-white p-6 text-center">
            <Lock :size="32" class="mx-auto mb-2" />
            <h2 class="text-xl font-bold uppercase tracking-widest">Change Password</h2>
          </div>

          <!-- Body -->
          <div class="p-8">
            <p class="text-gray-500 text-sm text-center mb-6 font-medium">
              Enter your current password and choose a new one.
            </p>

            <div v-if="error" class="mb-4 p-3 bg-red-50 border-2 border-red-600 text-red-600 text-sm font-bold">{{ error }}</div>

            <form @submit.prevent="handleSubmit" class="space-y-5">
              <div>
                <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Current Password</label>
                <div class="relative">
                  <input
                    v-model="form.current_password"
                    :type="showCurrent ? 'text' : 'password'"
                    placeholder="Enter current password"
                    class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none pr-12"
                  />
                  <button type="button" @click="showCurrent = !showCurrent" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-black">
                    <Eye v-if="!showCurrent" :size="20" />
                    <EyeOff v-else :size="20" />
                  </button>
                </div>
              </div>

              <div>
                <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">New Password</label>
                <div class="relative">
                  <input
                    v-model="form.new_password"
                    :type="showNew ? 'text' : 'password'"
                    placeholder="At least 6 characters"
                    class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none pr-12"
                  />
                  <button type="button" @click="showNew = !showNew" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-black">
                    <Eye v-if="!showNew" :size="20" />
                    <EyeOff v-else :size="20" />
                  </button>
                </div>
              </div>

              <div>
                <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Confirm New Password</label>
                <div class="relative">
                  <input
                    v-model="form.confirm_password"
                    :type="showConfirm ? 'text' : 'password'"
                    placeholder="Re-enter new password"
                    class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none pr-12"
                  />
                  <button type="button" @click="showConfirm = !showConfirm" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-black">
                    <Eye v-if="!showConfirm" :size="20" />
                    <EyeOff v-else :size="20" />
                  </button>
                </div>
              </div>

              <button
                type="submit"
                :disabled="loading"
                class="w-full py-4 bg-black text-white font-bold uppercase tracking-widest text-sm hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
              >
                {{ loading ? 'Changing...' : 'Change Password' }}
              </button>
            </form>

            <button
              @click="router.back()"
              class="w-full mt-4 py-3 bg-white text-black border-2 border-black font-bold uppercase tracking-widest text-sm hover:bg-gray-100 transition-colors inline-flex items-center justify-center gap-2"
            >
              <ArrowLeft :size="16" /> Back
            </button>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>
