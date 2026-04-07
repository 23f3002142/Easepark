<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import StatCard from '@/components/StatCard.vue'
import { getDashboard, type DashboardData } from '@/api/user.api'
import { Car, Clock, BarChart3, Bell, MapPin, ArrowRight } from 'lucide-vue-next'

const data = ref<DashboardData | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    data.value = await getDashboard()
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load dashboard'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <DashboardLayout>
    <div v-if="loading" class="flex items-center justify-center py-32">
      <div class="w-8 h-8 border-4 border-black border-t-transparent animate-spin"></div>
    </div>

    <div v-else-if="error" class="py-16 text-center">
      <p class="text-red-600 font-bold text-lg">{{ error }}</p>
    </div>

    <div v-else-if="data">
      <!-- Welcome -->
      <div class="mb-8">
        <h1 class="text-3xl md:text-4xl font-bold tracking-tighter text-black">
          Welcome back, <span class="underline decoration-4">{{ data.user.username }}</span>
        </h1>
        <p class="text-lg text-gray-500 font-medium mt-2">Manage your parking quickly and easily</p>
      </div>

      <!-- Quick Actions -->
      <div class="flex flex-wrap gap-3 mb-10">
        <RouterLink
          to="/book"
          class="inline-flex items-center gap-2 px-6 py-3 bg-black text-white font-bold uppercase tracking-wider text-sm hover:bg-gray-800 transition-colors"
        >
          <Car :size="18" /> Book a Spot
        </RouterLink>
        <RouterLink
          to="/bookings"
          class="inline-flex items-center gap-2 px-6 py-3 bg-white text-black border-2 border-black font-bold uppercase tracking-wider text-sm hover:bg-gray-100 transition-colors"
        >
          <Clock :size="18" /> My Bookings
        </RouterLink>
        <RouterLink
          to="/summary"
          class="inline-flex items-center gap-2 px-6 py-3 bg-white text-black border-2 border-black font-bold uppercase tracking-wider text-sm hover:bg-gray-100 transition-colors"
        >
          <BarChart3 :size="18" /> Summary
        </RouterLink>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left Column -->
        <div class="lg:col-span-2 space-y-8">
          <!-- Stats Row -->
          <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
            <StatCard label="Total Bookings" :value="data.user.total_bookings" />
            <StatCard label="Active Now" :value="data.active_bookings.length" />
            <StatCard label="Nearby Lots" :value="data.available_lots.length" />
          </div>

          <!-- Active Bookings -->
          <div class="bg-white border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <h2 class="text-xl font-bold text-black uppercase tracking-tight mb-4">Active Bookings</h2>
            <div v-if="data.active_bookings.length" class="space-y-3">
              <div
                v-for="booking in data.active_bookings"
                :key="booking.reservation_id"
                class="flex items-center justify-between p-4 border-2 border-gray-200 hover:border-black transition-colors"
              >
                <div>
                  <p class="font-bold text-black">{{ booking.lot_name }}</p>
                  <p class="text-sm text-gray-500 font-medium">Spot {{ booking.spot_number }} &bull; {{ booking.date }}</p>
                </div>
                <div class="text-right">
                  <p class="text-sm font-mono text-gray-600">{{ booking.time_range }}</p>
                  <RouterLink
                    :to="`/release/${booking.reservation_id}`"
                    class="text-sm font-bold text-red-600 hover:underline"
                  >
                    Release
                  </RouterLink>
                </div>
              </div>
            </div>
            <div v-else class="py-8 text-center border-2 border-dashed border-gray-300">
              <p class="text-gray-400 font-medium">No active bookings</p>
              <RouterLink to="/book" class="text-black font-bold text-sm hover:underline mt-2 inline-block">Book a spot to get started &rarr;</RouterLink>
            </div>
          </div>

          <!-- Profile Info -->
          <div class="bg-white border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <h2 class="text-xl font-bold text-black uppercase tracking-tight mb-4">Profile</h2>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p class="text-gray-500 font-medium">Full Name</p>
                <p class="font-bold text-black">{{ data.user.full_name || data.user.username }}</p>
              </div>
              <div>
                <p class="text-gray-500 font-medium">Member Since</p>
                <p class="font-bold text-black">{{ data.user.member_since ? new Date(data.user.member_since).toLocaleDateString() : 'N/A' }}</p>
              </div>
              <div>
                <p class="text-gray-500 font-medium">Email</p>
                <p class="font-bold text-black font-mono text-xs">{{ data.user.email }}</p>
              </div>
              <div>
                <p class="text-gray-500 font-medium">Total Bookings</p>
                <p class="font-bold text-black">{{ data.user.total_bookings }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Sidebar -->
        <div class="space-y-6">
          <!-- Nearby Lots -->
          <div class="bg-white border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <h2 class="text-lg font-bold text-black uppercase tracking-tight mb-4">
              <MapPin :size="16" class="inline mr-1" /> Nearby Lots
            </h2>
            <div v-if="data.available_lots.length" class="space-y-3">
              <div
                v-for="lot in data.available_lots"
                :key="lot.id"
                class="flex items-center justify-between py-2 border-b border-gray-200 last:border-0"
              >
                <div>
                  <p class="font-bold text-black text-sm">{{ lot.name }}</p>
                  <p class="text-xs text-gray-500">{{ lot.free_spots }} / {{ lot.total_spots }} available</p>
                </div>
                <span class="text-xs font-bold px-2 py-1 bg-gray-100 border border-gray-300">{{ lot.free_spots }} free</span>
              </div>
            </div>
            <p v-else class="text-sm text-gray-400">Update your pin code in profile to see lots near you.</p>
            <RouterLink
              to="/book"
              class="mt-4 w-full inline-flex items-center justify-center gap-2 px-4 py-2 bg-black text-white text-sm font-bold uppercase tracking-wider hover:bg-gray-800 transition-colors"
            >
              Search Lots <ArrowRight :size="14" />
            </RouterLink>
          </div>

          <!-- Notifications -->
          <div class="bg-white border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <h2 class="text-lg font-bold text-black uppercase tracking-tight mb-4">
              <Bell :size="16" class="inline mr-1" /> Notifications
            </h2>
            <div v-if="data.notifications.length" class="space-y-2">
              <div
                v-for="(note, i) in data.notifications"
                :key="i"
                class="p-3 bg-gray-50 border border-gray-200 text-sm text-gray-600"
              >
                {{ note }}
              </div>
            </div>
            <p v-else class="text-sm text-gray-400">No new notifications.</p>
          </div>

          <!-- Quick Actions -->
          <div class="bg-white border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <h2 class="text-lg font-bold text-black uppercase tracking-tight mb-4">Quick Actions</h2>
            <div class="space-y-2">
              <RouterLink to="/book" class="block w-full text-center py-2 border-2 border-black font-bold text-sm uppercase tracking-wider hover:bg-black hover:text-white transition-colors">Reserve Spot</RouterLink>
              <RouterLink to="/bookings" class="block w-full text-center py-2 border-2 border-black font-bold text-sm uppercase tracking-wider hover:bg-black hover:text-white transition-colors">View History</RouterLink>
              <RouterLink to="/profile/edit" class="block w-full text-center py-2 border-2 border-black font-bold text-sm uppercase tracking-wider hover:bg-black hover:text-white transition-colors">Edit Profile</RouterLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>
