<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import PaginationBar from '@/components/PaginationBar.vue'
import { getDashboard, deleteLot, getSpot, type AdminLot, type AdminSpotBrief } from '@/api/admin.api'
import { useToast } from '@/composables/useToast'
import { Plus, Edit, Trash2, X, User, Car, Clock, DollarSign } from 'lucide-vue-next'

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

// Spot detail card state
const spotDetail = ref<any>(null)
const spotDetailLoading = ref(false)
const spotDetailError = ref('')
const activeSpotId = ref<number | null>(null)

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

async function handleSpotClick(spot: AdminSpotBrief, lot: AdminLot) {
  if (activeSpotId.value === spot.id) {
    closeSpotDetail()
    return
  }
  activeSpotId.value = spot.id
  spotDetailLoading.value = true
  spotDetailError.value = ''
  spotDetail.value = null
  try {
    const res = await getSpot(spot.id)
    spotDetail.value = { ...res.spot, lot_name: lot.parking_name, lot_price: lot.price }
  } catch (err: any) {
    spotDetailError.value = err.response?.data?.error || 'Failed to load spot details'
  } finally {
    spotDetailLoading.value = false
  }
}

function closeSpotDetail() {
  activeSpotId.value = null
  spotDetail.value = null
  spotDetailError.value = ''
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', hour12: true
  })
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

          <!-- Spot visualization — clickable buttons -->
          <div class="flex flex-wrap gap-1.5 mb-4">
            <button
              v-for="spot in lot.spots"
              :key="spot.id"
              @click="handleSpotClick(spot, lot)"
              :class="[
                'w-7 h-7 text-[10px] font-bold flex items-center justify-center border-2 transition-all cursor-pointer',
                spot.status === 'A'
                  ? 'bg-green-100 border-green-400 text-green-700 hover:bg-green-200 hover:border-green-600'
                  : 'bg-red-100 border-red-400 text-red-700 hover:bg-red-200 hover:border-red-600',
                activeSpotId === spot.id ? 'ring-2 ring-black ring-offset-1 scale-110' : ''
              ]"
              :title="`Spot ${spot.spot_number} — ${spot.status === 'A' ? 'Available' : 'Occupied'}`"
            >
              {{ spot.status }}
            </button>
          </div>

          <!-- Legend -->
          <div class="flex items-center gap-4 text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-4">
            <span class="flex items-center gap-1"><span class="w-3 h-3 bg-green-100 border border-green-400 inline-block"></span> Available</span>
            <span class="flex items-center gap-1"><span class="w-3 h-3 bg-red-100 border border-red-400 inline-block"></span> Occupied</span>
          </div>

          <!-- Spot Detail Card (inline) -->
          <transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="opacity-0 -translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition duration-150 ease-in"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 -translate-y-2"
          >
            <div v-if="activeSpotId && spotDetail && lot.spots.some(s => s.id === activeSpotId)" class="mb-4 border-2 border-black bg-gray-50 p-4 relative">
              <button @click="closeSpotDetail" class="absolute top-2 right-2 text-gray-400 hover:text-black">
                <X :size="16" />
              </button>

              <div v-if="spotDetailLoading" class="py-4 text-center">
                <div class="w-5 h-5 border-2 border-black border-t-transparent animate-spin mx-auto"></div>
              </div>

              <div v-else-if="spotDetailError" class="text-red-600 text-sm font-bold">{{ spotDetailError }}</div>

              <div v-else-if="spotDetail">
                <!-- Available Spot -->
                <div v-if="spotDetail.status === 'A'">
                  <div class="flex items-center gap-2 mb-3">
                    <span class="w-3 h-3 bg-green-500 rounded-full"></span>
                    <h4 class="font-bold text-black uppercase tracking-tight text-sm">Spot {{ spotDetail.spot_number }} — Available</h4>
                  </div>
                  <div class="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span class="text-gray-400 font-bold uppercase tracking-wider text-[10px]">Lot</span>
                      <p class="font-bold text-black">{{ spotDetail.lot_name }}</p>
                    </div>
                    <div>
                      <span class="text-gray-400 font-bold uppercase tracking-wider text-[10px]">Price</span>
                      <p class="font-bold text-black">₹{{ spotDetail.lot_price }}/hr</p>
                    </div>
                    <div>
                      <span class="text-gray-400 font-bold uppercase tracking-wider text-[10px]">Status</span>
                      <p class="font-bold text-green-600">Ready for booking</p>
                    </div>
                    <div>
                      <span class="text-gray-400 font-bold uppercase tracking-wider text-[10px]">Active</span>
                      <p class="font-bold text-black">{{ spotDetail.is_active ? 'Yes' : 'No' }}</p>
                    </div>
                  </div>
                </div>

                <!-- Occupied Spot -->
                <div v-else>
                  <div class="flex items-center gap-2 mb-3">
                    <span class="w-3 h-3 bg-red-500 rounded-full"></span>
                    <h4 class="font-bold text-black uppercase tracking-tight text-sm">Spot {{ spotDetail.spot_number }} — Occupied</h4>
                  </div>

                  <div v-if="spotDetail.reservation" class="space-y-2">
                    <div class="grid grid-cols-2 gap-2 text-xs">
                      <div class="flex items-start gap-1.5">
                        <User :size="12" class="mt-0.5 text-gray-400 shrink-0" />
                        <div>
                          <span class="text-gray-400 font-bold uppercase tracking-wider text-[10px]">User</span>
                          <p class="font-bold text-black">{{ spotDetail.reservation.username }}</p>
                        </div>
                      </div>
                      <div class="flex items-start gap-1.5">
                        <Car :size="12" class="mt-0.5 text-gray-400 shrink-0" />
                        <div>
                          <span class="text-gray-400 font-bold uppercase tracking-wider text-[10px]">Vehicle</span>
                          <p class="font-bold text-black font-mono">{{ spotDetail.reservation.vehicle_number }}</p>
                        </div>
                      </div>
                      <div class="flex items-start gap-1.5">
                        <Clock :size="12" class="mt-0.5 text-gray-400 shrink-0" />
                        <div>
                          <span class="text-gray-400 font-bold uppercase tracking-wider text-[10px]">Since</span>
                          <p class="font-bold text-black">{{ formatDate(spotDetail.reservation.booking_time) }}</p>
                        </div>
                      </div>
                      <div class="flex items-start gap-1.5">
                        <DollarSign :size="12" class="mt-0.5 text-gray-400 shrink-0" />
                        <div>
                          <span class="text-gray-400 font-bold uppercase tracking-wider text-[10px]">Est. Cost</span>
                          <p class="font-bold text-black">₹{{ spotDetail.reservation.estimated_cost }} ({{ spotDetail.reservation.duration_hours }}h)</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <p v-else class="text-xs text-gray-400 font-medium">No active reservation details found.</p>
                </div>
              </div>
            </div>
          </transition>

          <!-- Spot Detail Loading (for this lot's spots) -->
          <div v-if="activeSpotId && spotDetailLoading && lot.spots.some(s => s.id === activeSpotId)" class="mb-4 border-2 border-gray-300 bg-gray-50 p-4">
            <div class="py-2 text-center">
              <div class="w-5 h-5 border-2 border-black border-t-transparent animate-spin mx-auto mb-2"></div>
              <p class="text-xs text-gray-400 font-bold">Loading spot details...</p>
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
