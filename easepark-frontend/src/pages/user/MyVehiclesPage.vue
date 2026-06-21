<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import {
  getVehicles, addVehicle, deleteVehicle, setDefaultVehicle,
  type Vehicle
} from '@/api/user.api'
import { useToast } from '@/composables/useToast'
import { Plus, Trash2, Star, Car, ShieldCheck } from 'lucide-vue-next'

const toast = useToast()

const vehicles = ref<Vehicle[]>([])
const loading = ref(true)
const error = ref('')

// Form state
const newVehicleNumber = ref('')
const newNickname = ref('')
const newIsDefault = ref(false)
const formError = ref('')
const formFieldErrors = ref<Record<string, string[]>>({})
const submitting = ref(false)

async function fetchVehicles() {
  try {
    const res = await getVehicles()
    vehicles.value = res.vehicles
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load vehicles'
  } finally {
    loading.value = false
  }
}

onMounted(fetchVehicles)

async function handleAddVehicle() {
  if (!newVehicleNumber.value.trim()) {
    formError.value = 'Vehicle number is required'
    return
  }

  submitting.value = true
  formError.value = ''
  formFieldErrors.value = {}

  try {
    const res = await addVehicle({
      vehicle_number: newVehicleNumber.value.trim().toUpperCase(),
      nickname: newNickname.value.trim() || undefined,
      is_default: newIsDefault.value,
    })
    toast.success(res.message)
    // Reset form
    newVehicleNumber.value = ''
    newNickname.value = ''
    newIsDefault.value = false
    // Refresh list
    await fetchVehicles()
  } catch (err: any) {
    if (err.response?.status === 422) {
      formFieldErrors.value = err.response.data.errors || {}
    } else {
      formError.value = err.response?.data?.error || 'Failed to add vehicle'
    }
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id: number) {
  if (!confirm('Are you sure you want to delete this vehicle?')) return
  try {
    const res = await deleteVehicle(id)
    toast.success(res.message)
    await fetchVehicles()
  } catch (err: any) {
    toast.error(err.response?.data?.error || 'Failed to delete vehicle')
  }
}

async function handleSetDefault(id: number) {
  try {
    const res = await setDefaultVehicle(id)
    toast.success(res.message)
    await fetchVehicles()
  } catch (err: any) {
    toast.error(err.response?.data?.error || 'Failed to set default vehicle')
  }
}
</script>

<template>
  <DashboardLayout>
    <PageHeader title="My Vehicles" subtitle="Save and manage your vehicles for faster parking bookings" />

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="w-8 h-8 border-4 border-black border-t-transparent animate-spin"></div>
    </div>

    <div v-else-if="error" class="py-16 text-center">
      <p class="text-red-600 font-bold text-lg">{{ error }}</p>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Add Vehicle Form (Left/Top) -->
      <div class="lg:col-span-1">
        <div class="bg-white border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <h3 class="text-xl font-bold text-black uppercase tracking-tight mb-4 flex items-center gap-2">
            <Plus :size="20" /> Add Vehicle
          </h3>

          <div v-if="formError" class="mb-4 p-3 bg-red-50 border-2 border-red-600 text-red-600 text-xs font-bold">
            {{ formError }}
          </div>

          <form @submit.prevent="handleAddVehicle" class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-black uppercase tracking-wider mb-1.5">Vehicle Number</label>
              <input
                v-model="newVehicleNumber"
                type="text"
                placeholder="e.g. DL01CA1234"
                class="w-full px-4 py-2.5 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none text-sm font-medium uppercase font-mono"
              />
              <p v-if="formFieldErrors.vehicle_number" class="text-red-600 text-xs font-bold mt-1">
                {{ formFieldErrors.vehicle_number[0] }}
              </p>
            </div>

            <div>
              <label class="block text-xs font-bold text-black uppercase tracking-wider mb-1.5">Nickname (Optional)</label>
              <input
                v-model="newNickname"
                type="text"
                placeholder="e.g. My Sedan, Wife's SUV"
                class="w-full px-4 py-2.5 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none text-sm font-medium"
              />
              <p v-if="formFieldErrors.nickname" class="text-red-600 text-xs font-bold mt-1">
                {{ formFieldErrors.nickname[0] }}
              </p>
            </div>

            <div class="flex items-center gap-2.5 pt-2">
              <input
                v-model="newIsDefault"
                type="checkbox"
                id="is-default"
                class="w-4 h-4 text-black border-2 border-black rounded focus:ring-0 focus:ring-offset-0"
              />
              <label for="is-default" class="text-xs font-bold text-black uppercase tracking-wider cursor-pointer select-none">
                Set as Default Vehicle
              </label>
            </div>

            <button
              type="submit"
              :disabled="submitting"
              class="w-full py-3 bg-black text-white font-bold uppercase tracking-wider text-sm hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
            >
              {{ submitting ? 'Adding...' : 'Add Vehicle' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Saved Vehicles List (Right/Bottom) -->
      <div class="lg:col-span-2 space-y-4">
        <h3 class="text-xl font-bold text-black uppercase tracking-tight mb-2">
          Saved Vehicles ({{ vehicles.length }})
        </h3>

        <div v-if="!vehicles.length" class="py-16 text-center border-2 border-dashed border-gray-300 bg-gray-50">
          <Car :size="48" class="mx-auto mb-3 text-gray-400" />
          <p class="text-gray-400 font-bold text-lg">No vehicles saved yet</p>
          <p class="text-gray-400 text-sm mt-1">Add a vehicle on the left to get started.</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="v in vehicles"
            :key="v.id"
            class="bg-white border-2 border-black p-5 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex flex-col justify-between"
          >
            <div>
              <div class="flex justify-between items-start mb-2">
                <span class="font-mono font-bold text-lg text-black bg-gray-100 border border-gray-300 px-2 py-0.5 uppercase tracking-wide">
                  {{ v.vehicle_number }}
                </span>
                <span
                  v-if="v.is_default"
                  class="inline-flex items-center gap-1 px-2.5 py-0.5 bg-green-500 border border-black text-[10px] font-bold uppercase tracking-wider text-black shadow-[1px_1px_0px_0px_rgba(0,0,0,1)]"
                >
                  <ShieldCheck :size="10" /> Default
                </span>
              </div>
              <p class="font-bold text-black text-sm uppercase tracking-tight">
                {{ v.nickname || 'Unnamed Vehicle' }}
              </p>
            </div>

            <div class="flex items-center gap-3 mt-6 pt-3 border-t border-gray-100">
              <button
                v-if="!v.is_default"
                @click="handleSetDefault(v.id)"
                class="flex-1 py-1.5 bg-white border-2 border-black text-black hover:bg-gray-50 text-xs font-bold uppercase tracking-wider transition-colors flex items-center justify-center gap-1.5"
              >
                <Star :size="12" /> Make Default
              </button>
              <button
                @click="handleDelete(v.id)"
                class="py-1.5 px-3 bg-red-500 border-2 border-black text-black hover:bg-red-600 text-xs font-bold uppercase transition-colors flex items-center justify-center"
              >
                <Trash2 :size="12" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>
