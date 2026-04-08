<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import PaginationBar from '@/components/PaginationBar.vue'
import { getNotifications, markNotificationsRead, clearAllNotifications, type NotificationItem } from '@/api/notification.api'
import { useToast } from '@/composables/useToast'
import { Bell, Check, Trash2 } from 'lucide-vue-next'

const toast = useToast()

const notifications = ref<NotificationItem[]>([])
const unreadCount = ref(0)
const loading = ref(true)
const page = ref(1)
const totalPages = ref(0)
const totalItems = ref(0)

async function fetchNotifications(p = 1) {
  loading.value = true
  try {
    const res = await getNotifications({ page: p, per_page: 15 })
    notifications.value = res.notifications
    unreadCount.value = res.unread_count
    page.value = res.pagination.page
    totalPages.value = res.pagination.total_pages
    totalItems.value = res.pagination.total_items
  } catch {
    toast.error('Failed to load notifications')
  } finally {
    loading.value = false
  }
}

async function markAllRead() {
  try {
    await markNotificationsRead()
    notifications.value.forEach(n => { n.is_read = true })
    unreadCount.value = 0
    toast.success('All notifications marked as read')
  } catch {
    toast.error('Failed to mark notifications as read')
  }
}

async function clearAll() {
  try {
    await clearAllNotifications()
    notifications.value = []
    unreadCount.value = 0
    totalItems.value = 0
    totalPages.value = 0
    toast.success('All notifications cleared')
  } catch {
    toast.error('Failed to clear notifications')
  }
}

function timeAgo(dateStr: string | null): string {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  if (days < 30) return `${days}d ago`
  return new Date(dateStr).toLocaleDateString()
}

const typeStyles: Record<string, { bg: string; text: string; icon: string }> = {
  success: { bg: 'bg-green-50 border-green-200', text: 'text-green-700', icon: '✓' },
  warning: { bg: 'bg-yellow-50 border-yellow-200', text: 'text-yellow-700', icon: '⚠' },
  error: { bg: 'bg-red-50 border-red-200', text: 'text-red-700', icon: '✕' },
  info: { bg: 'bg-gray-50 border-gray-200', text: 'text-gray-700', icon: 'ℹ' },
}

onMounted(() => fetchNotifications())
</script>

<template>
  <DashboardLayout>
    <PageHeader title="Notifications" :subtitle="`${totalItems} notification${totalItems !== 1 ? 's' : ''} · ${unreadCount} unread`" />

    <!-- Actions -->
    <div class="flex items-center gap-3 mb-6">
      <button
        v-if="unreadCount > 0"
        @click="markAllRead"
        class="flex items-center gap-2 px-4 py-2 bg-black text-white text-xs font-bold uppercase tracking-wider hover:bg-gray-800 transition-colors"
      >
        <Check :size="14" />
        Mark all read
      </button>
      <button
        v-if="totalItems > 0"
        @click="clearAll"
        class="flex items-center gap-2 px-4 py-2 bg-white text-red-600 border-2 border-red-600 text-xs font-bold uppercase tracking-wider hover:bg-red-50 transition-colors"
      >
        <Trash2 :size="14" />
        Clear all
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="w-8 h-8 border-4 border-black border-t-transparent animate-spin"></div>
    </div>

    <!-- Empty -->
    <div v-else-if="notifications.length === 0" class="py-20 text-center">
      <Bell :size="48" class="mx-auto text-gray-300 mb-4" />
      <p class="text-lg font-bold text-gray-400">No notifications</p>
      <p class="text-sm text-gray-300 mt-1">You're all caught up!</p>
    </div>

    <!-- List -->
    <div v-else class="space-y-3">
      <div
        v-for="n in notifications"
        :key="n.id"
        :class="[
          'border-2 p-4 md:p-5 transition-colors',
          n.is_read
            ? 'bg-white border-gray-200'
            : 'bg-gray-50 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]'
        ]"
      >
        <div class="flex items-start gap-3">
          <span
            :class="[
              'w-8 h-8 flex items-center justify-center text-sm font-bold shrink-0 border',
              (typeStyles[n.type] || typeStyles.info).bg,
              (typeStyles[n.type] || typeStyles.info).text,
            ]"
          >
            {{ (typeStyles[n.type] || typeStyles.info).icon }}
          </span>
          <div class="min-w-0 flex-1">
            <div class="flex items-center justify-between gap-2">
              <h3 :class="['text-sm font-bold', n.is_read ? 'text-gray-700' : 'text-black']">{{ n.title }}</h3>
              <div class="flex items-center gap-2 shrink-0">
                <span v-if="!n.is_read" class="w-2 h-2 bg-black rounded-full"></span>
                <span class="text-[10px] text-gray-400 font-medium">{{ timeAgo(n.created_at) }}</span>
              </div>
            </div>
            <p class="text-xs text-gray-500 mt-1">{{ n.message }}</p>
          </div>
        </div>
      </div>
    </div>

    <PaginationBar
      v-if="totalPages > 1"
      :page="page"
      :total-pages="totalPages"
      @change="fetchNotifications"
      class="mt-6"
    />
  </DashboardLayout>
</template>
