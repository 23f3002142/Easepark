<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import PaginationBar from '@/components/PaginationBar.vue'
import { getHistory, getReceiptUrl } from '@/api/user.api'
import type { Reservation, Pagination } from '@/types/parking'

const history = ref<Reservation[]>([])
const pagination = ref<Pagination>({ page: 1, per_page: 7, total_pages: 0, total_items: 0 })
const loading = ref(true)
const error = ref('')

async function fetchHistory(page = 1) {
  loading.value = true
  try {
    const res = await getHistory({ page, per_page: 7 })
    history.value = res.history
    pagination.value = res.pagination
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load booking history'
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchHistory())

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', hour12: true
  })
}

function onPageChange(p: number) {
  fetchHistory(p)
}

function statusColor(status: string) {
  if (status === 'active') return 'bg-green-100 text-green-700 border-green-300'
  if (status === 'pending') return 'bg-yellow-100 text-yellow-700 border-yellow-300'
  if (status === 'completed') return 'bg-gray-100 text-gray-600 border-gray-300'
  if (status === 'cancelled') return 'bg-red-100 text-red-600 border-red-300'
  return 'bg-gray-100 text-gray-500 border-gray-200'
}
</script>

<template>
  <DashboardLayout>
    <PageHeader title="Booking History" subtitle="View all your past and current bookings" />

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="w-8 h-8 border-4 border-black border-t-transparent animate-spin"></div>
    </div>

    <div v-else-if="error" class="py-16 text-center">
      <p class="text-red-600 font-bold">{{ error }}</p>
    </div>

    <div v-else>
      <div v-if="history.length">
        <!-- Desktop: Table -->
        <div class="hidden md:block overflow-x-auto">
          <table class="w-full border-2 border-black">
            <thead>
              <tr class="bg-black text-white">
                <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider">Spot</th>
                <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider">Lot Name</th>
                <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider">Vehicle</th>
                <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider hidden lg:table-cell">From</th>
                <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider hidden lg:table-cell">To</th>
                <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Cost</th>
                <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Status</th>
                <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="res in history"
                :key="res.id"
                class="border-b border-gray-200 hover:bg-gray-50 transition-colors"
              >
                <td class="px-4 py-4 font-bold">{{ res.spot_number }}</td>
                <td class="px-4 py-4 font-bold text-black">{{ res.lot_name }}</td>
                <td class="px-4 py-4 font-mono text-sm">{{ res.vehicle_number || 'N/A' }}</td>
                <td class="px-4 py-4 text-sm text-gray-600 hidden lg:table-cell">{{ formatDate(res.booking_timestamp) }}</td>
                <td class="px-4 py-4 text-sm text-gray-600 hidden lg:table-cell">{{ res.releasing_timestamp ? formatDate(res.releasing_timestamp) : '—' }}</td>
                <td class="px-4 py-4 text-center font-bold">{{ res.total_cost != null ? `₹${res.total_cost}` : '—' }}</td>
                <td class="px-4 py-4 text-center">
                  <span :class="['px-2 py-1 text-xs font-bold uppercase tracking-wider border rounded', statusColor(res.status)]">
                    {{ res.status }}
                  </span>
                </td>
                <td class="px-4 py-4 text-center">
                  <div class="flex items-center justify-center gap-2 flex-wrap">
                    <RouterLink
                      v-if="res.status === 'active'"
                      :to="`/release/${res.id}`"
                      class="px-3 py-1 bg-black text-white text-xs font-bold uppercase tracking-wider hover:bg-gray-800 transition-colors inline-block"
                    >
                      Release & Pay
                    </RouterLink>
                    <a
                      v-if="res.status === 'completed'"
                      :href="getReceiptUrl(res.id)"
                      target="_blank"
                      class="px-3 py-1 bg-black text-white text-xs font-bold uppercase tracking-wider hover:bg-gray-800 transition-colors inline-block"
                    >
                      Receipt
                    </a>
                    <span v-if="res.status === 'cancelled'" class="text-xs text-gray-400">—</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile: Card layout -->
        <div class="md:hidden space-y-3">
          <div
            v-for="res in history"
            :key="res.id"
            class="border-2 border-black bg-white p-4"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <span class="font-bold text-black text-base">{{ res.lot_name }}</span>
                <span class="text-xs font-bold text-gray-500">Spot {{ res.spot_number }}</span>
              </div>
              <span :class="['px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider border rounded', statusColor(res.status)]">
                {{ res.status }}
              </span>
            </div>
            <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-xs mb-3">
              <div>
                <span class="text-gray-400 font-bold uppercase tracking-wider text-[10px]">Vehicle</span>
                <p class="font-mono font-bold text-black">{{ res.vehicle_number || 'N/A' }}</p>
              </div>
              <div>
                <span class="text-gray-400 font-bold uppercase tracking-wider text-[10px]">Cost</span>
                <p class="font-bold text-black">{{ res.total_cost != null ? `₹${res.total_cost}` : '—' }}</p>
              </div>
              <div>
                <span class="text-gray-400 font-bold uppercase tracking-wider text-[10px]">From</span>
                <p class="text-gray-600">{{ formatDate(res.booking_timestamp) }}</p>
              </div>
              <div>
                <span class="text-gray-400 font-bold uppercase tracking-wider text-[10px]">To</span>
                <p class="text-gray-600">{{ res.releasing_timestamp ? formatDate(res.releasing_timestamp) : '—' }}</p>
              </div>
            </div>
            <div class="flex gap-2">
              <RouterLink
                v-if="res.status === 'active'"
                :to="`/release/${res.id}`"
                class="flex-1 py-2 bg-black text-white text-xs font-bold uppercase tracking-wider text-center hover:bg-gray-800 transition-colors"
              >
                Release & Pay
              </RouterLink>
              <a
                v-if="res.status === 'completed'"
                :href="getReceiptUrl(res.id)"
                target="_blank"
                class="flex-1 py-2 bg-black text-white text-xs font-bold uppercase tracking-wider text-center hover:bg-gray-800 transition-colors"
              >
                Receipt
              </a>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="py-12 md:py-16 text-center border-2 border-dashed border-gray-300">
        <p class="text-gray-400 font-bold text-base md:text-lg">No bookings yet</p>
        <RouterLink to="/book" class="text-black font-bold text-xs md:text-sm hover:underline mt-2 inline-block">Book a spot to get started &rarr;</RouterLink>
      </div>

      <PaginationBar
        :page="pagination.page"
        :total-pages="pagination.total_pages"
        @change="onPageChange"
      />
    </div>

  </DashboardLayout>
</template>
