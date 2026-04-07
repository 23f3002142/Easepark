<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import { getProfile } from '@/api/admin.api'
import type { User } from '@/types/user'
import { Settings, Lock } from 'lucide-vue-next'

const user = ref<User | null>(null)
const loading = ref(true)
const error = ref('')

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
      <PageHeader title="Admin Profile" :subtitle="`Member since ${user.member_since ? new Date(user.member_since).toLocaleDateString() : 'N/A'}`" />

      <div class="bg-white border-2 border-black p-8 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <div class="space-y-6">
          <div v-for="field in fields" :key="field.key" class="flex flex-col sm:flex-row sm:items-center border-b border-gray-200 pb-4 last:border-0 last:pb-0">
            <span class="text-sm font-bold text-gray-500 uppercase tracking-wider w-40 mb-1 sm:mb-0">{{ field.label }}</span>
            <span class="font-bold text-black text-lg">{{ (user as any)[field.key] || 'N/A' }}</span>
          </div>
        </div>

        <div class="mt-8 flex items-center justify-center gap-4 flex-wrap">
          <RouterLink
            to="/admin/profile/edit"
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
