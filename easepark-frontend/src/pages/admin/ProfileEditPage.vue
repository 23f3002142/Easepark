<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import { getProfile, updateProfile } from '@/api/admin.api'
import { useAuthStore } from '@/stores/auth.store'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  full_name: '',
  username: '',
  email: '',
  phone_number: '',
  address: '',
  pin_code: '',
})
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')

onMounted(async () => {
  try {
    const res = await getProfile()
    form.value = {
      full_name: res.user.full_name || '',
      username: res.user.username || '',
      email: res.user.email || '',
      phone_number: res.user.phone_number || '',
      address: res.user.address || '',
      pin_code: res.user.pin_code || '',
    }
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load profile'
  } finally {
    loading.value = false
  }
})

async function handleSubmit() {
  error.value = ''
  success.value = ''
  saving.value = true
  try {
    const res = await updateProfile(form.value)
    success.value = res.message
    authStore.user = res.user
    setTimeout(() => router.push('/admin/profile'), 1200)
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to update profile'
  } finally {
    saving.value = false
  }
}

const fields = [
  { label: 'Full Name', key: 'full_name', type: 'text' },
  { label: 'Username', key: 'username', type: 'text' },
  { label: 'Email', key: 'email', type: 'email' },
  { label: 'Phone Number', key: 'phone_number', type: 'text' },
  { label: 'Address', key: 'address', type: 'textarea' },
  { label: 'Pin Code', key: 'pin_code', type: 'text' },
] as const
</script>

<template>
  <DashboardLayout>
    <div v-if="loading" class="flex items-center justify-center py-32">
      <div class="w-8 h-8 border-4 border-black border-t-transparent animate-spin"></div>
    </div>

    <div v-else class="max-w-2xl mx-auto">
      <PageHeader title="Edit Admin Profile" subtitle="Update your personal information" />

      <div class="bg-white border-2 border-black p-8 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <div v-if="error" class="mb-6 p-4 bg-red-50 border-2 border-red-600 text-red-600 text-sm font-bold">{{ error }}</div>
        <div v-if="success" class="mb-6 p-4 bg-green-50 border-2 border-green-600 text-green-600 text-sm font-bold">{{ success }}</div>

        <form @submit.prevent="handleSubmit" class="space-y-5">
          <div v-for="field in fields" :key="field.key">
            <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">{{ field.label }}</label>
            <textarea
              v-if="field.type === 'textarea'"
              v-model="(form as any)[field.key]"
              rows="3"
              class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none transition-all text-sm font-medium"
            ></textarea>
            <input
              v-else
              v-model="(form as any)[field.key]"
              :type="field.type"
              class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none transition-all text-sm font-medium"
            />
          </div>

          <div class="flex gap-4 pt-4">
            <button
              type="submit"
              :disabled="saving"
              class="flex-1 py-3 bg-black text-white font-bold uppercase tracking-widest text-sm hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
            >
              {{ saving ? 'Saving...' : 'Update' }}
            </button>
            <button
              type="button"
              @click="router.push('/admin/profile')"
              class="flex-1 py-3 bg-white text-black border-2 border-black font-bold uppercase tracking-widest text-sm hover:bg-gray-100 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </DashboardLayout>
</template>
