<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import StatCard from '@/components/StatCard.vue'
import { getSummary, type AdminSummary } from '@/api/admin.api'
import Chart from 'chart.js/auto'
import { BarChart3, TrendingUp, Users, MapPin, Clock } from 'lucide-vue-next'

const data = ref<AdminSummary | null>(null)
const loading = ref(true)
const error = ref('')

const occupancyRef = ref<HTMLCanvasElement | null>(null)
const monthlyRef = ref<HTMLCanvasElement | null>(null)
const registrationRef = ref<HTMLCanvasElement | null>(null)
const topLotsRef = ref<HTMLCanvasElement | null>(null)
const avgTimeRef = ref<HTMLCanvasElement | null>(null)

let charts: Chart[] = []

const hasOccupancy = computed(() => data.value && data.value.total_spots > 0)
const hasMonthly = computed(() => data.value && data.value.months?.length > 0)
const hasRegistrations = computed(() => data.value && data.value.registration_labels?.length > 0)
const hasTopLots = computed(() => data.value && data.value.top_lot_labels?.length > 0)
const hasAvgTime = computed(() => data.value && data.value.avg_time_labels?.length > 0)

const gridColor = 'rgba(148, 163, 184, 0.22)'
const axisTickColor = '#334155'
const monthlyPalette = ['#2563EB', '#0EA5E9', '#14B8A6', '#22C55E', '#84CC16', '#F59E0B', '#F97316']
const registrationsPalette = ['#8B5CF6', '#A855F7', '#EC4899', '#F43F5E', '#6366F1']
const topLotsPalette = ['#0D9488', '#14B8A6', '#06B6D4', '#0284C7', '#22C55E', '#65A30D']
const avgTimePalette = ['#F59E0B', '#F97316', '#FB7185', '#A855F7', '#6366F1']

function getCycledColors(length: number, palette: string[]) {
  return Array.from({ length }, (_, idx) => palette[idx % palette.length])
}

onMounted(async () => {
  try {
    data.value = await getSummary()
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load summary'
  } finally {
    loading.value = false
    await nextTick()
    renderCharts()
  }
})

function renderCharts() {
  charts.forEach(c => c.destroy())
  charts = []
  if (!data.value) return

  if (occupancyRef.value && hasOccupancy.value) {
    charts.push(new Chart(occupancyRef.value, {
      type: 'doughnut',
      data: {
        labels: ['Occupied', 'Available'],
        datasets: [{
          data: [data.value.occupied_spots, data.value.available_spots],
          backgroundColor: ['#F97316', '#22C55E'],
          borderColor: ['#C2410C', '#15803D'],
          borderWidth: 1,
          hoverOffset: 10,
          spacing: 2
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: axisTickColor }
          },
          title: {
            display: true,
            text: 'Current Parking Occupancy',
            color: '#0F172A',
            font: { weight: 'bold' }
          }
        }
      }
    }))
  }

  if (monthlyRef.value && hasMonthly.value) {
    charts.push(new Chart(monthlyRef.value, {
      type: 'bar',
      data: {
        labels: data.value.months,
        datasets: [{
          label: 'Vehicles Parked',
          data: data.value.bookings_per_month,
          backgroundColor: getCycledColors(data.value.bookings_per_month.length, monthlyPalette),
          borderColor: '#1E3A8A',
          borderWidth: 1,
          borderRadius: 8,
          maxBarThickness: 40
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Monthly Parking Usage',
            color: '#0F172A',
            font: { weight: 'bold' }
          }
        },
        scales: {
          x: {
            ticks: { color: axisTickColor },
            grid: { color: gridColor }
          },
          y: {
            beginAtZero: true,
            ticks: { precision: 0, color: axisTickColor },
            grid: { color: gridColor }
          }
        }
      }
    }))
  }

  if (registrationRef.value && hasRegistrations.value) {
    charts.push(new Chart(registrationRef.value, {
      type: 'bar',
      data: {
        labels: data.value.registration_labels,
        datasets: [{
          label: 'New Users',
          data: data.value.registration_data,
          backgroundColor: getCycledColors(data.value.registration_data.length, registrationsPalette),
          borderColor: '#6D28D9',
          borderWidth: 1,
          borderRadius: 8,
          maxBarThickness: 40
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: 'User Registration Stats',
            color: '#0F172A',
            font: { weight: 'bold' }
          }
        },
        scales: {
          x: {
            ticks: { color: axisTickColor },
            grid: { color: gridColor }
          },
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1, color: axisTickColor },
            grid: { color: gridColor }
          }
        }
      }
    }))
  }

  if (topLotsRef.value && hasTopLots.value) {
    charts.push(new Chart(topLotsRef.value, {
      type: 'bar',
      data: {
        labels: data.value.top_lot_labels,
        datasets: [{
          label: 'Usage Count',
          data: data.value.top_lot_data,
          backgroundColor: getCycledColors(data.value.top_lot_data.length, topLotsPalette),
          borderColor: '#0F766E',
          borderWidth: 1,
          borderRadius: 8,
          maxBarThickness: 32
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Top Parking Locations by Usage',
            color: '#0F172A',
            font: { weight: 'bold' }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: { color: axisTickColor },
            grid: { color: gridColor }
          },
          y: {
            ticks: { color: axisTickColor },
            grid: { color: gridColor }
          }
        }
      }
    }))
  }

  if (avgTimeRef.value && hasAvgTime.value) {
    charts.push(new Chart(avgTimeRef.value, {
      type: 'bar',
      data: {
        labels: data.value.avg_time_labels,
        datasets: [{
          label: 'Avg Parking Time (hrs)',
          data: data.value.avg_time_data,
          backgroundColor: getCycledColors(data.value.avg_time_data.length, avgTimePalette),
          borderColor: '#C2410C',
          borderWidth: 1,
          borderRadius: 8,
          maxBarThickness: 36
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Average Parking Time per Lot (hours)',
            color: '#0F172A',
            font: { weight: 'bold' }
          }
        },
        scales: {
          x: {
            ticks: { color: axisTickColor },
            grid: { color: gridColor }
          },
          y: {
            beginAtZero: true,
            ticks: { color: axisTickColor },
            grid: { color: gridColor }
          }
        }
      }
    }))
  }
}
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
      <PageHeader title="Parking Statistics Dashboard" subtitle="A quick overview of parking occupancy, trends, and user activity insights" />

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4 mb-10">
        <StatCard label="Total Spots" :value="data.total_spots" />
        <StatCard label="Occupied" :value="data.occupied_spots" />
        <StatCard label="Available" :value="data.available_spots" />
      </div>

      <!-- First Row: Occupancy + Monthly + Registration -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        <!-- Occupancy Doughnut -->
        <div class="bg-gradient-to-br from-white to-orange-50 border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <template v-if="hasOccupancy">
            <canvas ref="occupancyRef"></canvas>
          </template>
          <div v-else class="flex flex-col items-center justify-center py-12 text-center">
            <BarChart3 :size="40" class="text-gray-300 mb-4" />
            <h3 class="font-bold text-black uppercase tracking-tight text-sm mb-2">Current Parking Occupancy</h3>
            <p class="text-gray-400 text-sm max-w-xs">No parking spots have been created yet. Add parking lots to start tracking occupancy.</p>
          </div>
        </div>

        <div class="space-y-8">
          <!-- Monthly Parking -->
          <div class="bg-gradient-to-br from-white to-blue-50 border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <template v-if="hasMonthly">
              <canvas ref="monthlyRef"></canvas>
            </template>
            <div v-else class="flex flex-col items-center justify-center py-8 text-center">
              <TrendingUp :size="36" class="text-gray-300 mb-3" />
              <h3 class="font-bold text-black uppercase tracking-tight text-sm mb-2">Monthly Parking Usage</h3>
              <p class="text-gray-400 text-sm max-w-xs">No bookings recorded yet. Usage trends will appear here once users start parking.</p>
            </div>
          </div>

          <!-- User Registrations -->
          <div class="bg-gradient-to-br from-white to-violet-50 border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <template v-if="hasRegistrations">
              <canvas ref="registrationRef"></canvas>
            </template>
            <div v-else class="flex flex-col items-center justify-center py-8 text-center">
              <Users :size="36" class="text-gray-300 mb-3" />
              <h3 class="font-bold text-black uppercase tracking-tight text-sm mb-2">User Registration Stats</h3>
              <p class="text-gray-400 text-sm max-w-xs">No user registrations in the last 12 months. Registration trends will show here.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Divider -->
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-black uppercase tracking-tighter">Advanced Insights</h2>
        <div class="w-24 h-1 bg-gradient-to-r from-emerald-500 via-blue-500 to-violet-500 mx-auto mt-2"></div>
      </div>

      <!-- Second Row: Top Lots + Avg Time -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        <div class="bg-gradient-to-br from-white to-teal-50 border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <template v-if="hasTopLots">
            <canvas ref="topLotsRef"></canvas>
          </template>
          <div v-else class="flex flex-col items-center justify-center py-12 text-center">
            <MapPin :size="36" class="text-gray-300 mb-3" />
            <h3 class="font-bold text-black uppercase tracking-tight text-sm mb-2">Top Parking Locations</h3>
            <p class="text-gray-400 text-sm max-w-xs">No booking data available yet. The most popular lots will be displayed here once bookings begin.</p>
            <div class="mt-4 p-3 bg-gray-50 border border-gray-200 text-xs text-gray-500 max-w-xs">
              <strong>Tip:</strong> Share your parking lots with users so they can start booking and you can track which lots are most popular.
            </div>
          </div>
        </div>

        <div class="bg-gradient-to-br from-white to-amber-50 border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <template v-if="hasAvgTime">
            <canvas ref="avgTimeRef"></canvas>
          </template>
          <div v-else class="flex flex-col items-center justify-center py-12 text-center">
            <Clock :size="36" class="text-gray-300 mb-3" />
            <h3 class="font-bold text-black uppercase tracking-tight text-sm mb-2">Average Parking Time</h3>
            <p class="text-gray-400 text-sm max-w-xs">Average parking duration per lot will appear here once users complete and release bookings.</p>
            <div class="mt-4 p-3 bg-gray-50 border border-gray-200 text-xs text-gray-500 max-w-xs">
              <strong>Tip:</strong> Completed bookings (with release time) contribute to duration analytics. Encourage users to release spots when done.
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>
