<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import StatCard from '@/components/StatCard.vue'
import { getUserHistory, type UserHistory } from '@/api/admin.api'

const route = useRoute()
const router = useRouter()
const userId = Number(route.params.id)

const data = ref<UserHistory | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    data.value = await getUserHistory(userId)
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load user history'
  } finally {
    loading.value = false
  }
})

function formatDate(iso: string | null) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', hour12: true
  })
}
</script>

<template>
  <DashboardLayout>
    <div v-if="loading" class="flex items-center justify-center py-32">
      <div class="w-8 h-8 border-4 border-black border-t-transparent animate-spin"></div>
    </div>

    <div v-else-if="error" class="py-16 text-center">
      <p class="text-red-600 font-bold text-lg">{{ error }}</p>
      <button @click="router.push('/admin/users')" class="mt-4 px-6 py-3 bg-black text-white font-bold uppercase tracking-wider text-sm">Back to Users</button>
    </div>

    <div v-else-if="data">
      <div class="flex items-center gap-4 mb-2">
        <button @click="router.push('/admin/users')" class="text-sm font-bold text-gray-500 hover:text-black uppercase tracking-wider">&larr; Back to Users</button>
      </div>

      <PageHeader
        :title="`${data.user.full_name || data.user.username}'s Booking History`"
        :subtitle="`${data.user.email} &bull; Member since ${formatDate(data.user.member_since)}`"
      />

      <!-- Stats -->
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-10">
        <StatCard label="Total Paid" :value="data.total_amount_paid" prefix="₹" />
        <StatCard label="Hours Parked" :value="data.total_duration_hours" />
        <StatCard label="Total Bookings" :value="data.total_bookings" />
        <StatCard label="First Booking" :value="formatDate(data.first_booking)" />
        <StatCard label="Latest Booking" :value="formatDate(data.latest_booking)" />
      </div>

      <!-- History Table -->
      <div v-if="data.history.length" class="overflow-x-auto">
        <table class="w-full border-2 border-black">
          <thead>
            <tr class="bg-black text-white">
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider">Spot</th>
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider">Lot</th>
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider hidden md:table-cell">Vehicle</th>
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider hidden lg:table-cell">From</th>
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider hidden lg:table-cell">To</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Cost</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="res in data.history" :key="res.id" class="border-b border-gray-200 hover:bg-gray-50">
              <td class="px-4 py-3 font-bold">{{ res.spot_number }}</td>
              <td class="px-4 py-3 font-bold">{{ res.lot_name }}</td>
              <td class="px-4 py-3 font-mono text-sm hidden md:table-cell">{{ res.vehicle_number || 'N/A' }}</td>
              <td class="px-4 py-3 text-sm text-gray-600 hidden lg:table-cell">{{ formatDateTime(res.booking_timestamp) }}</td>
              <td class="px-4 py-3 text-sm text-gray-600 hidden lg:table-cell">{{ res.releasing_timestamp ? formatDateTime(res.releasing_timestamp) : '—' }}</td>
              <td class="px-4 py-3 text-center font-bold">{{ res.total_cost != null ? `₹${res.total_cost}` : '—' }}</td>
              <td class="px-4 py-3 text-center">
                <span :class="[
                  'px-2 py-1 text-xs font-bold uppercase tracking-wider',
                  res.status === 'active' ? 'bg-green-100 text-green-800 border border-green-300' :
                  res.status === 'completed' ? 'bg-gray-100 text-gray-800 border border-gray-300' :
                  'bg-yellow-100 text-yellow-800 border border-yellow-300'
                ]">{{ res.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="py-12 text-center border-2 border-dashed border-gray-300">
        <p class="text-gray-400 font-bold">This user has no bookings yet.</p>
      </div>
    </div>
  </DashboardLayout>
</template>
