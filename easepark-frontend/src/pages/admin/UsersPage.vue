<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import PaginationBar from '@/components/PaginationBar.vue'
import { getUsers } from '@/api/admin.api'
import type { User } from '@/types/user'
import type { Pagination } from '@/types/parking'
import { Eye, Search } from 'lucide-vue-next'

const users = ref<User[]>([])
const loading = ref(true)
const error = ref('')

const searchQuery = ref('')
const page = ref(1)
const perPage = ref(10)
const pagination = ref<Pagination>({ page: 1, per_page: 10, total_pages: 0, total_items: 0 })

async function fetchUsers(p = 1) {
  loading.value = true
  error.value = ''
  try {
    const res = await getUsers({
      page: p,
      per_page: perPage.value,
      search: searchQuery.value.trim() || undefined
    })
    users.value = res.users
    pagination.value = res.pagination
    page.value = p
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load users'
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchUsers(1))

function handleSearch() {
  fetchUsers(1)
}

function onPageChange(p: number) {
  fetchUsers(p)
}
</script>

<template>
  <DashboardLayout>
    <PageHeader title="Registered Users" subtitle="View and manage all registered users" />

    <!-- Search -->
    <form @submit.prevent="handleSearch" class="flex gap-3 mb-8">
      <div class="relative flex-1">
        <Search :size="18" class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by username, email, or name..."
          class="w-full pl-12 pr-4 py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none text-sm font-medium"
        />
      </div>
      <button type="submit" class="px-6 py-3 bg-black text-white font-bold uppercase tracking-wider text-sm hover:bg-gray-800 transition-colors">
        Search
      </button>
    </form>

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="w-8 h-8 border-4 border-black border-t-transparent animate-spin"></div>
    </div>

    <div v-else-if="error" class="py-16 text-center">
      <p class="text-red-600 font-bold">{{ error }}</p>
    </div>

    <div v-else>
      <div v-if="users.length" class="overflow-x-auto">
        <table class="w-full border-2 border-black mb-6">
          <thead>
            <tr class="bg-black text-white">
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider">#</th>
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider">Email</th>
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider">Username</th>
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider hidden md:table-cell">Full Name</th>
              <th class="px-4 py-3 text-left text-sm font-bold uppercase tracking-wider hidden lg:table-cell">Phone</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider hidden lg:table-cell">Pin</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Bookings</th>
              <th class="px-4 py-3 text-center text-sm font-bold uppercase tracking-wider">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(user, idx) in users"
              :key="user.id"
              class="border-b border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <td class="px-4 py-4 font-bold text-gray-400">{{ (pagination.page - 1) * pagination.per_page + idx + 1 }}</td>
              <td class="px-4 py-4 font-mono text-sm">{{ user.email }}</td>
              <td class="px-4 py-4 font-bold text-black">{{ user.username }}</td>
              <td class="px-4 py-4 text-sm hidden md:table-cell">{{ user.full_name || 'N/A' }}</td>
              <td class="px-4 py-4 text-sm font-mono hidden lg:table-cell">{{ user.phone_number || 'N/A' }}</td>
              <td class="px-4 py-4 text-center text-sm hidden lg:table-cell">{{ user.pin_code || 'N/A' }}</td>
              <td class="px-4 py-4 text-center font-bold">{{ user.total_bookings }}</td>
              <td class="px-4 py-4 text-center">
                <RouterLink
                  :to="`/admin/users/${user.id}/history`"
                  class="inline-flex items-center gap-1 px-3 py-1 bg-black text-white text-xs font-bold uppercase tracking-wider hover:bg-gray-800 transition-colors"
                >
                  <Eye :size="12" /> History
                </RouterLink>
              </td>
            </tr>
          </tbody>
        </table>

        <PaginationBar
          :page="pagination.page"
          :total-pages="pagination.total_pages"
          @change="onPageChange"
        />
      </div>

      <div v-else class="py-16 text-center border-2 border-dashed border-gray-300">
        <p class="text-gray-400 font-bold text-lg">No registered users found</p>
      </div>
    </div>
  </DashboardLayout>
</template>
