<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import StatCard from '@/components/StatCard.vue'
import PaginationBar from '@/components/PaginationBar.vue'
import { getSummary, downloadSummaryReport, type SummaryData } from '@/api/user.api'
import Chart from 'chart.js/auto'
import { Download, FileText } from 'lucide-vue-next'

const data = ref<SummaryData | null>(null)
const loading = ref(true)
const error = ref('')

const bookingChartRef = ref<HTMLCanvasElement | null>(null)
const durationChartRef = ref<HTMLCanvasElement | null>(null)
const spentChartRef = ref<HTMLCanvasElement | null>(null)

let charts: Chart[] = []

async function fetchSummary(page = 1) {
  loading.value = true
  try {
    data.value = await getSummary({ page })
    await nextTick()
    renderCharts()
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load summary'
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchSummary())

function renderCharts() {
  charts.forEach(c => c.destroy())
  charts = []
  if (!data.value) return

  if (bookingChartRef.value) {
    charts.push(new Chart(bookingChartRef.value, {
      type: 'bar',
      data: {
        labels: data.value.chart_labels,
        datasets: [{
          label: 'Bookings',
          data: data.value.chart_data,
          backgroundColor: 'rgba(0,0,0,0.8)',
          borderColor: '#000',
          borderWidth: 1
        }]
      },
      options: { responsive: true, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
    }))
  }

  if (durationChartRef.value) {
    charts.push(new Chart(durationChartRef.value, {
      type: 'doughnut',
      data: {
        labels: data.value.chart_duration_labels,
        datasets: [{
          data: data.value.chart_duration_data,
          backgroundColor: ['#000', '#333', '#555', '#777', '#999', '#bbb', '#ddd'],
          borderColor: '#fff',
          borderWidth: 2
        }]
      },
      options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
    }))
  }

  if (spentChartRef.value) {
    charts.push(new Chart(spentChartRef.value, {
      type: 'bar',
      data: {
        labels: data.value.chart_booking_labels,
        datasets: [
          {
            type: 'bar',
            label: 'Time Parked (hrs)',
            data: data.value.chart_duration_data_each,
            backgroundColor: 'rgba(0,0,0,0.7)',
            borderColor: '#000',
            borderWidth: 1,
            yAxisID: 'y'
          },
          {
            type: 'line',
            label: 'Total Cost (₹)',
            data: data.value.chart_cost_data_each,
            borderColor: '#666',
            backgroundColor: 'rgba(100,100,100,0.1)',
            tension: 0.4,
            fill: false,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        scales: {
          y: { type: 'linear', position: 'left', title: { display: true, text: 'Hours Parked' } },
          y1: { type: 'linear', position: 'right', grid: { drawOnChartArea: false }, title: { display: true, text: 'Cost (₹)' } }
        }
      }
    }))
  }
}

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

function onPageChange(p: number) {
  fetchSummary(p)
}

// Report download state
const reportFrom = ref('')
const reportTo = ref('')
const reportLoading = ref(false)
const reportError = ref('')

function getDefaultDates() {
  const now = new Date()
  const firstDay = new Date(now.getFullYear(), now.getMonth(), 1)
  reportFrom.value = firstDay.toISOString().split('T')[0]
  reportTo.value = now.toISOString().split('T')[0]
}
getDefaultDates()

async function handleReportDownload() {
  if (!reportFrom.value || !reportTo.value) {
    reportError.value = 'Please select both from and to dates'
    return
  }
  if (reportFrom.value > reportTo.value) {
    reportError.value = 'From date must be before To date'
    return
  }
  reportLoading.value = true
  reportError.value = ''
  try {
    await downloadSummaryReport(reportFrom.value, reportTo.value)
  } catch (err: any) {
    reportError.value = err.response?.data?.error || 'Failed to generate report'
  } finally {
    reportLoading.value = false
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
      <PageHeader
        :title="`Booking Summary for ${data.user.full_name || data.user.username}`"
        subtitle="Insight into your parking history, time usage, and spending behavior"
      />

      <!-- Stats Cards -->
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-10">
        <StatCard label="Total Paid" :value="data.total_amount_paid" prefix="₹" />
        <StatCard label="Hours Parked" :value="data.total_duration_hours" />
        <StatCard label="Total Bookings" :value="data.total_bookings" />
        <StatCard label="First Booking" :value="formatDate(data.first_booking)" />
        <StatCard label="Latest Booking" :value="formatDate(data.latest_booking)" />
      </div>

      <!-- Booking History Table -->
      <div v-if="data.history.length" class="mb-12">
        <h2 class="text-2xl font-bold text-black uppercase tracking-tighter mb-6">Booking Details</h2>
        <div class="overflow-x-auto">
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
        <PaginationBar :page="data.pagination.page" :total-pages="data.pagination.total_pages" @change="onPageChange" />
      </div>

      <div v-else class="mb-12 py-8 text-center border-2 border-dashed border-gray-300">
        <p class="text-gray-400 font-bold">No bookings yet.</p>
      </div>

      <!-- Monthly Report Download -->
      <div class="mb-12 bg-white border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <div class="flex items-center gap-2 mb-4">
          <FileText :size="20" />
          <h2 class="text-xl font-bold text-black uppercase tracking-tight">Download Monthly Report</h2>
        </div>
        <p class="text-sm text-gray-500 mb-4">Select a date range to generate a PDF analysis report of your bookings.</p>

        <div v-if="reportError" class="mb-4 p-3 bg-red-50 border-2 border-red-600 text-red-600 text-sm font-bold">{{ reportError }}</div>

        <div class="flex flex-col sm:flex-row items-end gap-4">
          <div class="flex-1 w-full">
            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">From</label>
            <input
              v-model="reportFrom"
              type="date"
              class="w-full px-4 py-2.5 border-2 border-black text-sm font-medium focus:outline-none focus:ring-2 focus:ring-black"
            />
          </div>
          <div class="flex-1 w-full">
            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">To</label>
            <input
              v-model="reportTo"
              type="date"
              class="w-full px-4 py-2.5 border-2 border-black text-sm font-medium focus:outline-none focus:ring-2 focus:ring-black"
            />
          </div>
          <button
            @click="handleReportDownload"
            :disabled="reportLoading"
            class="inline-flex items-center gap-2 px-6 py-2.5 bg-black text-white font-bold uppercase tracking-wider text-sm hover:bg-gray-800 disabled:bg-gray-400 transition-colors whitespace-nowrap"
          >
            <Download :size="16" /> {{ reportLoading ? 'Generating...' : 'Download PDF' }}
          </button>
        </div>
      </div>

      <!-- Charts -->
      <h2 class="text-2xl font-bold text-black uppercase tracking-tighter mb-6 text-center">User Statistics</h2>
      <p class="text-center text-gray-500 mb-8">Insight into your parking history, time usage, and spending behavior</p>

      <div v-if="data.total_bookings > 0" class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        <!-- Donut Chart -->
        <div class="bg-white border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <h3 class="font-bold text-black uppercase tracking-tight mb-4 text-center">Parking Duration Distribution</h3>
          <canvas ref="durationChartRef"></canvas>
        </div>

        <div class="space-y-8">
          <!-- Spent vs Time Chart -->
          <div class="bg-white border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <h3 class="font-bold text-black uppercase tracking-tight mb-4 text-center">Total Spent vs Time Parked</h3>
            <canvas ref="spentChartRef"></canvas>
          </div>

          <!-- Booking Timeline Chart -->
          <div class="bg-white border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <h3 class="font-bold text-black uppercase tracking-tight mb-4 text-center">Booking History Timeline</h3>
            <canvas ref="bookingChartRef"></canvas>
          </div>
        </div>
      </div>
      <div v-else class="py-12 text-center border-2 border-dashed border-gray-300 mb-12">
        <p class="text-gray-400 font-bold text-lg">No booking data to chart yet</p>
        <p class="text-gray-400 text-sm mt-1">Make your first booking to see statistics here.</p>
      </div>
    </div>
  </DashboardLayout>
</template>
