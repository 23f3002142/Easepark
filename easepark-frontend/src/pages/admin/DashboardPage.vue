<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import PaginationBar from '@/components/PaginationBar.vue'
import { getDashboard, deleteLot, type AdminLot } from '@/api/admin.api'
import { useToast } from '@/composables/useToast'
import { Plus, Edit, Trash2 } from 'lucide-vue-next'

const toast = useToast()
const lots = ref<AdminLot[]>([])
const loading = ref(true)
const error = ref('')
const page = ref(1)
const perPage = 9

const totalPages = computed(() => Math.ceil(lots.value.length / perPage))
const paginatedLots = computed(() => {
  const start = (page.value - 1) * perPage
  return lots.value.slice(start, start + perPage)
})

async function fetchDashboard() {
  loading.value = true
  try {
    const res = await getDashboard()
    lots.value = res.lots
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load dashboard'
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchDashboard())

async function handleDelete(lotId: number, lotName: string) {
  if (!confirm(`Are you sure you want to delete "${lotName}"? This will remove all its spots too.`)) return
  try {
    await deleteLot(lotId)
    toast.success(`Lot "${lotName}" deleted successfully`)
    lots.value = lots.value.filter(l => l.id !== lotId)
    if (paginatedLots.value.length === 0 && page.value > 1) page.value--
  } catch (err: any) {
    toast.error(err.response?.data?.error || 'Failed to delete lot')
  }
}

function spotColor(occupied: number, total: number) {
  const ratio = total > 0 ? occupied / total : 0
  if (ratio >= 0.8) return 'text-red-600'
  if (ratio >= 0.5) return 'text-yellow-600'
  return 'text-green-600'
}
</script>

<template>
  <DashboardLayout>
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 gap-4">
      <PageHeader title="Admin Dashboard" subtitle="Manage your parking lots and spots" />
      <RouterLink
        to="/admin/lots/add"
        class="inline-flex items-center gap-2 px-6 py-3 bg-black text-white font-bold uppercase tracking-wider text-sm hover:bg-gray-800 transition-colors self-start"
      >
        <Plus :size="18" /> Add Lot
      </RouterLink>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-32">
      <div class="w-8 h-8 border-4 border-black border-t-transparent animate-spin"></div>
    </div>

    <div v-else-if="error" class="py-16 text-center">
      <p class="text-red-600 font-bold text-lg">{{ error }}</p>
    </div>

    <div v-else>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="(lot, idx) in paginatedLots"
          :key="lot.id"
          class="bg-white border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex flex-col"
        >
          <div class="flex items-start justify-between mb-4">
            <div>
              <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">Parking #{{ (page - 1) * perPage + idx + 1 }}</p>
              <h3 class="text-lg font-bold text-black mt-1">{{ lot.parking_name }}</h3>
            </div>
            <span :class="['text-sm font-bold', spotColor(lot.occupied_spots, lot.total_spots)]">
              {{ lot.occupied_spots }}/{{ lot.total_spots }} occupied
            </span>
          </div>

          <div class="text-sm text-gray-500 space-y-1 mb-4">
            <p><span class="font-bold text-black">Address:</span> {{ lot.address }}</p>
            <p><span class="font-bold text-black">Pin:</span> {{ lot.pin_code }} &bull; <span class="font-bold text-black">Price:</span> ₹{{ lot.price }}/hr</p>
          </div>

          <!-- Spot visualization -->
          <div class="flex flex-wrap gap-1 mb-4">
            <div
              v-for="i in lot.total_spots"
              :key="i"
              :class="[
                'w-6 h-6 text-[10px] font-bold flex items-center justify-center border',
                i <= lot.available_spots ? 'bg-green-100 border-green-400 text-green-700' : 'bg-red-100 border-red-400 text-red-700'
              ]"
            >
              {{ i <= lot.available_spots ? 'A' : 'O' }}
            </div>
          </div>

          <div class="mt-auto flex gap-2">
            <RouterLink
              :to="`/admin/lots/${lot.id}/edit`"
              class="flex-1 text-center py-2 border-2 border-black font-bold text-xs uppercase tracking-wider hover:bg-black hover:text-white transition-colors inline-flex items-center justify-center gap-1"
            >
              <Edit :size="12" /> Edit
            </RouterLink>
            <button
              @click="handleDelete(lot.id, lot.parking_name)"
              class="flex-1 text-center py-2 border-2 border-red-600 text-red-600 font-bold text-xs uppercase tracking-wider hover:bg-red-600 hover:text-white transition-colors inline-flex items-center justify-center gap-1"
            >
              <Trash2 :size="12" /> Delete
            </button>
          </div>
        </div>
      </div>

      <PaginationBar v-if="totalPages > 1" :page="page" :total-pages="totalPages" @change="(p: number) => page = p" class="mt-6" />

      <div v-if="!lots.length" class="py-16 text-center border-2 border-dashed border-gray-300 mt-4">
        <p class="text-gray-400 font-bold text-lg">No parking lots yet</p>
        <RouterLink to="/admin/lots/add" class="text-black font-bold text-sm hover:underline mt-2 inline-block">Add your first lot &rarr;</RouterLink>
      </div>
    </div>
  </DashboardLayout>
</template>
