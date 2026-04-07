<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import PaginationBar from '@/components/PaginationBar.vue'
import { getLots, reserveSpot } from '@/api/user.api'
import { useToast } from '@/composables/useToast'
import type { ParkingLot, Pagination } from '@/types/parking'
import { Search } from 'lucide-vue-next'

const toast = useToast()

const router = useRouter()

const lots = ref<ParkingLot[]>([])
const pagination = ref<Pagination>({ page: 1, per_page: 6, total_pages: 0, total_items: 0 })
const searchQuery = ref('')
const loading = ref(true)
const error = ref('')

// Reserve modal state
const showModal = ref(false)
const selectedLot = ref<ParkingLot | null>(null)
const vehicleNumber = ref('')
const reserveLoading = ref(false)
const reserveError = ref('')

async function fetchLots(page = 1) {
  loading.value = true
  error.value = ''
  try {
    const res = await getLots({ search: searchQuery.value, page, per_page: 6 })
    lots.value = res.lots
    pagination.value = res.pagination
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load lots'
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchLots())

function handleSearch() {
  fetchLots(1)
}

function onPageChange(p: number) {
  fetchLots(p)
}

function openReserve(lot: ParkingLot) {
  selectedLot.value = lot
  vehicleNumber.value = ''
  reserveError.value = ''
  showModal.value = true
}

// Route calculation loader
const routeLoading = ref(false)
const routeMessage = ref('')
const routeMessages = [
  'Finding the best spot for you...',
  'Calculating route to parking...',
  'Reserving your spot...',
  'Almost there...',
]

async function handleReserve() {
  if (!selectedLot.value || !vehicleNumber.value.trim()) {
    reserveError.value = 'Vehicle number is required'
    return
  }
  reserveLoading.value = true
  reserveError.value = ''
  showModal.value = false
  routeLoading.value = true
  routeMessage.value = routeMessages[0]

  // Cycle through messages for UX
  let msgIdx = 0
  const msgInterval = setInterval(() => {
    msgIdx = (msgIdx + 1) % routeMessages.length
    routeMessage.value = routeMessages[msgIdx]
  }, 1500)

  try {
    const res = await reserveSpot(selectedLot.value.id, vehicleNumber.value.trim())
    routeMessage.value = 'Spot reserved! Redirecting...'
    await new Promise(r => setTimeout(r, 1000))
    toast.success(res.message)
    router.push('/bookings')
  } catch (err: any) {
    reserveError.value = err.response?.data?.error || 'Failed to reserve spot'
    showModal.value = true
  } finally {
    clearInterval(msgInterval)
    reserveLoading.value = false
    routeLoading.value = false
  }
}
</script>

<template>
  <DashboardLayout>
    <PageHeader title="Book Your Spot" subtitle="Search lots by name, address, or pin code and reserve" />

    <!-- Search -->
    <form @submit.prevent="handleSearch" class="flex gap-3 mb-8">
      <div class="relative flex-1">
        <Search :size="18" class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by name, address or pin code..."
          class="w-full pl-12 pr-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none text-sm font-medium"
        />
      </div>
      <button type="submit" class="px-6 py-3 bg-black text-white font-bold uppercase tracking-wider text-sm hover:bg-gray-800 transition-colors">
        Search
      </button>
    </form>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="w-8 h-8 border-4 border-black border-t-transparent animate-spin"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="py-16 text-center">
      <p class="text-red-600 font-bold">{{ error }}</p>
    </div>

    <!-- Lots Table -->
    <div v-else>
      <div class="overflow-x-auto">
        <table class="w-full border-2 border-black">
          <thead>
            <tr class="bg-black text-white">
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider">Lot Name</th>
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider hidden md:table-cell">Address</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Pin Code</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Spots</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Available</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Price/hr</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="lot in lots"
              :key="lot.id"
              class="border-b border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <td class="px-4 py-4">
                <p class="font-bold text-black">{{ lot.name || lot.parking_name }}</p>
              </td>
              <td class="px-4 py-4 text-sm text-gray-600 hidden md:table-cell">{{ lot.address }}</td>
              <td class="px-4 py-4 text-center font-mono text-sm">{{ lot.pin_code }}</td>
              <td class="px-4 py-4 text-center font-bold">{{ lot.max_spots }}</td>
              <td class="px-4 py-4 text-center">
                <span :class="['font-bold', (lot.free_spots || 0) > 0 ? 'text-green-600' : 'text-red-600']">
                  {{ lot.free_spots || 0 }}
                </span>
              </td>
              <td class="px-4 py-4 text-center font-bold">&#8377;{{ lot.price }}</td>
              <td class="px-4 py-4 text-center">
                <button
                  v-if="(lot.free_spots || 0) > 0"
                  @click="openReserve(lot)"
                  class="px-4 py-2 bg-black text-white text-xs font-bold uppercase tracking-wider hover:bg-gray-800 transition-colors"
                >
                  Reserve
                </button>
                <span v-else class="text-xs font-bold text-gray-400 uppercase">Full</span>
              </td>
            </tr>
            <tr v-if="!lots.length">
              <td colspan="7" class="px-4 py-12 text-center text-gray-400 font-medium">
                No parking lots found matching your search.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <PaginationBar
        :page="pagination.page"
        :total-pages="pagination.total_pages"
        @change="onPageChange"
      />
    </div>

    <!-- Route Calculation Loader -->
    <teleport to="body">
      <transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="routeLoading" class="fixed inset-0 z-[110] flex flex-col items-center justify-center bg-white">
          <div class="text-center">
            <div class="relative w-24 h-24 mx-auto mb-8">
              <div class="absolute inset-0 border-4 border-gray-200 rounded-full"></div>
              <div class="absolute inset-0 border-4 border-black border-t-transparent rounded-full animate-spin"></div>
              <div class="absolute inset-3 border-4 border-gray-300 border-b-transparent rounded-full animate-spin" style="animation-direction: reverse; animation-duration: 1.5s;"></div>
            </div>
            <p class="text-2xl font-bold text-black tracking-tight mb-3">{{ routeMessage }}</p>
            <p class="text-sm text-gray-400 font-medium">Please wait while we set things up for you</p>
            <div class="mt-6 flex items-center justify-center gap-1.5">
              <div class="w-2 h-2 bg-black rounded-full animate-bounce" style="animation-delay: 0ms;"></div>
              <div class="w-2 h-2 bg-black rounded-full animate-bounce" style="animation-delay: 150ms;"></div>
              <div class="w-2 h-2 bg-black rounded-full animate-bounce" style="animation-delay: 300ms;"></div>
            </div>
          </div>
        </div>
      </transition>
    </teleport>

    <!-- Reserve Modal -->
    <teleport to="body">
      <transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 px-4">
          <div class="bg-white border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] w-full max-w-md p-8">
            <h3 class="text-2xl font-bold text-black uppercase tracking-tighter mb-2">Book the Parking Spot</h3>
            <p class="text-sm text-gray-500 mb-6">{{ selectedLot?.name || selectedLot?.parking_name }}</p>

            <div v-if="reserveError" class="mb-4 p-3 bg-red-50 border-2 border-red-600 text-red-600 text-sm font-bold">{{ reserveError }}</div>

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Lot Name</label>
                <input :value="selectedLot?.name || selectedLot?.parking_name" readonly class="w-full px-4 py-3 border-2 border-gray-300 bg-gray-100 text-sm font-medium" />
              </div>
              <div>
                <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Vehicle Number</label>
                <input
                  v-model="vehicleNumber"
                  type="text"
                  placeholder="MH12AB1234"
                  pattern="^[A-Z]{2}\d{1,2}[A-Z]{0,2}\d{1,4}$"
                  class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none text-sm font-medium uppercase"
                />
              </div>
            </div>

            <div class="flex gap-4 mt-8">
              <button
                @click="handleReserve"
                :disabled="reserveLoading"
                class="flex-1 py-3 bg-black text-white font-bold uppercase tracking-widest text-sm hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
              >
                {{ reserveLoading ? 'Reserving...' : 'Reserve' }}
              </button>
              <button
                @click="showModal = false"
                class="flex-1 py-3 bg-white text-black border-2 border-black font-bold uppercase tracking-widest text-sm hover:bg-gray-100 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </transition>
    </teleport>
  </DashboardLayout>
</template>
