<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import { getLot, editLot } from '@/api/admin.api'
import MapPicker from '@/components/MapPicker.vue'
import { useToast } from '@/composables/useToast'

const toast = useToast()

const route = useRoute()
const router = useRouter()
const lotId = Number(route.params.id)

const form = ref({
  parking_name: '',
  price: 0,
  address: '',
  pin_code: '',
  max_spots: 0,
  latitude: null as number | null,
  longitude: null as number | null,
})
const loading = ref(true)
const saving = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    const res = await getLot(lotId)
    form.value = {
      parking_name: res.lot.parking_name,
      price: res.lot.price,
      address: res.lot.address,
      pin_code: res.lot.pin_code,
      max_spots: res.lot.max_spots,
      latitude: res.lot.latitude,
      longitude: res.lot.longitude,
    }
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load lot'
  } finally {
    loading.value = false
  }
})

async function handleSubmit() {
  error.value = ''
  saving.value = true
  try {
    await editLot(lotId, form.value)
    toast.success('Parking lot updated successfully!')
    router.push('/admin')
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to update lot'
  } finally {
    saving.value = false
  }
}

const fields = [
  { label: 'Parking Name', key: 'parking_name', type: 'text' },
  { label: 'Price (₹ per hour)', key: 'price', type: 'number' },
  { label: 'Address', key: 'address', type: 'textarea' },
  { label: 'Pin Code', key: 'pin_code', type: 'text' },
  { label: 'Max Spots', key: 'max_spots', type: 'number' },
] as const
</script>

<template>
  <DashboardLayout>
    <div v-if="loading" class="flex items-center justify-center py-32">
      <div class="w-8 h-8 border-4 border-black border-t-transparent animate-spin"></div>
    </div>

    <div v-else class="max-w-2xl mx-auto">
      <PageHeader title="Edit Parking Lot" subtitle="Update parking lot details" />

      <div class="bg-white border-2 border-black p-8 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <div v-if="error" class="mb-6 p-4 bg-red-50 border-2 border-red-600 text-red-600 text-sm font-bold">{{ error }}</div>

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
              :step="field.type === 'number' ? 'any' : undefined"
              class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none transition-all text-sm font-medium"
            />
          </div>

          <!-- Map Picker for location -->
          <MapPicker
            :latitude="form.latitude"
            :longitude="form.longitude"
            @update:latitude="form.latitude = $event"
            @update:longitude="form.longitude = $event"
          />

          <div class="flex gap-4 pt-4">
            <button
              type="submit"
              :disabled="saving"
              class="flex-1 py-3 bg-black text-white font-bold uppercase tracking-widest text-sm hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
            >
              {{ saving ? 'Updating...' : 'Update' }}
            </button>
            <button
              type="button"
              @click="router.push('/admin')"
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
