<script setup lang="ts">
import { ref } from 'vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import { adminSearch } from '@/api/admin.api'
import { RouterLink } from 'vue-router'
import { Search } from 'lucide-vue-next'

const searchType = ref('user')
const query = ref('')
const results = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const searched = ref(false)

async function handleSearch() {
  if (!query.value.trim()) return
  loading.value = true
  error.value = ''
  searched.value = true
  try {
    const res = await adminSearch(searchType.value, query.value.trim())
    results.value = res.results
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Search failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <DashboardLayout>
    <PageHeader title="Search" subtitle="Search users, lots by name or pin code" />

    <!-- Search Form -->
    <div class="bg-white border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] mb-8">
      <form @submit.prevent="handleSearch" class="space-y-4">
        <div class="flex flex-col sm:flex-row gap-4">
          <div class="sm:w-48">
            <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Search Type</label>
            <select
              v-model="searchType"
              class="w-full px-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none text-sm font-bold bg-white"
            >
              <option value="user">User</option>
              <option value="lot_name">Lot Name</option>
              <option value="lot_number">Lot Pin Code</option>
            </select>
          </div>
          <div class="flex-1">
            <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Query</label>
            <div class="flex gap-3">
              <div class="relative flex-1">
                <Search :size="18" class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  v-model="query"
                  type="text"
                  placeholder="Enter search term..."
                  class="w-full pl-12 pr-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none text-sm font-medium"
                />
              </div>
              <button
                type="submit"
                :disabled="loading"
                class="px-6 py-3 bg-black text-white font-bold uppercase tracking-wider text-sm hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
              >
                {{ loading ? 'Searching...' : 'Search' }}
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>

    <!-- Error -->
    <div v-if="error" class="mb-6 p-4 bg-red-50 border-2 border-red-600 text-red-600 text-sm font-bold">{{ error }}</div>

    <!-- Results -->
    <div v-if="searched && !loading">
      <h2 class="text-xl font-bold text-black uppercase tracking-tight mb-4">
        Results <span class="text-gray-400">({{ results.length }})</span>
      </h2>

      <!-- User Results -->
      <div v-if="searchType === 'user' && results.length" class="overflow-x-auto">
        <table class="w-full border-2 border-black">
          <thead>
            <tr class="bg-black text-white">
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider">Username</th>
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider">Email</th>
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider hidden md:table-cell">Full Name</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Bookings</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in results" :key="u.id" class="border-b border-gray-200 hover:bg-gray-50">
              <td class="px-4 py-3 font-bold">{{ u.username }}</td>
              <td class="px-4 py-3 font-mono text-sm">{{ u.email }}</td>
              <td class="px-4 py-3 text-sm hidden md:table-cell">{{ u.full_name || 'N/A' }}</td>
              <td class="px-4 py-3 text-center font-bold">{{ u.total_bookings }}</td>
              <td class="px-4 py-3 text-center">
                <RouterLink
                  :to="`/admin/users/${u.id}/history`"
                  class="px-3 py-1 bg-black text-white text-xs font-bold uppercase tracking-wider hover:bg-gray-800 transition-colors inline-block"
                >
                  History
                </RouterLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Lot Results -->
      <div v-else-if="(searchType === 'lot_name' || searchType === 'lot_number') && results.length" class="overflow-x-auto">
        <table class="w-full border-2 border-black">
          <thead>
            <tr class="bg-black text-white">
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider">Lot Name</th>
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider hidden md:table-cell">Address</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Pin Code</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Spots</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Price/hr</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in results" :key="l.id" class="border-b border-gray-200 hover:bg-gray-50">
              <td class="px-4 py-3 font-bold">{{ l.parking_name }}</td>
              <td class="px-4 py-3 text-sm hidden md:table-cell">{{ l.address }}</td>
              <td class="px-4 py-3 text-center font-mono">{{ l.pin_code }}</td>
              <td class="px-4 py-3 text-center font-bold">{{ l.max_spots }}</td>
              <td class="px-4 py-3 text-center font-bold">₹{{ l.price }}</td>
              <td class="px-4 py-3 text-center">
                <RouterLink
                  :to="`/admin/lots/${l.id}/edit`"
                  class="px-3 py-1 bg-black text-white text-xs font-bold uppercase tracking-wider hover:bg-gray-800 transition-colors inline-block"
                >
                  Edit
                </RouterLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- No Results -->
      <div v-else-if="!results.length" class="py-12 text-center border-2 border-dashed border-gray-300">
        <p class="text-gray-400 font-bold">No results found for "{{ query }}"</p>
      </div>
    </div>
  </DashboardLayout>
</template>
