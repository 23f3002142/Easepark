<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Bell } from 'lucide-vue-next'
import { getNotifications, markNotificationsRead, type NotificationItem } from '@/api/notification.api'

const router = useRouter()
const open = ref(false)
const unreadCount = ref(0)
const notifications = ref<NotificationItem[]>([])
const loading = ref(false)
let pollInterval: ReturnType<typeof setInterval> | null = null

async function fetchNotifications() {
  try {
    const res = await getNotifications({ per_page: 8 })
    notifications.value = res.notifications
    unreadCount.value = res.unread_count
  } catch {
    // silent fail
  }
}

async function toggleDropdown() {
  open.value = !open.value
  if (open.value) {
    loading.value = true
    await fetchNotifications()
    loading.value = false
    // Mark visible ones as read
    const unreadIds = notifications.value.filter(n => !n.is_read).map(n => n.id)
    if (unreadIds.length) {
      try {
        await markNotificationsRead(unreadIds)
        notifications.value.forEach(n => { n.is_read = true })
        unreadCount.value = Math.max(0, unreadCount.value - unreadIds.length)
      } catch { /* silent */ }
    }
  }
}

function goToNotifications() {
  open.value = false
  router.push('/notifications')
}

function closeDropdown(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.notification-bell-wrapper')) {
    open.value = false
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
  return `${days}d ago`
}

const typeIcon: Record<string, string> = {
  success: '✓',
  warning: '⚠',
  error: '✕',
  info: 'ℹ',
}

onMounted(() => {
  fetchNotifications()
  pollInterval = setInterval(fetchNotifications, 30000)
  document.addEventListener('click', closeDropdown)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
  document.removeEventListener('click', closeDropdown)
})
</script>

<template>
  <div class="relative notification-bell-wrapper">
    <button
      @click="toggleDropdown"
      class="relative p-2 text-gray-600 hover:text-black transition-colors"
      title="Notifications"
    >
      <Bell :size="20" />
      <span
        v-if="unreadCount > 0"
        class="absolute -top-0.5 -right-0.5 w-5 h-5 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center"
      >
        {{ unreadCount > 9 ? '9+' : unreadCount }}
      </span>
    </button>

    <transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="open"
        class="absolute right-0 mt-2 w-80 max-h-[420px] bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] z-50 flex flex-col"
      >
        <div class="px-4 py-3 border-b-2 border-black bg-black text-white flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-widest">Notifications</span>
          <button
            @click="goToNotifications"
            class="text-[10px] font-bold uppercase tracking-wider text-white/70 hover:text-white"
          >
            View All
          </button>
        </div>

        <div v-if="loading" class="p-6 text-center">
          <div class="w-6 h-6 border-3 border-black border-t-transparent animate-spin mx-auto"></div>
        </div>

        <div v-else-if="notifications.length === 0" class="p-6 text-center text-sm text-gray-400 font-medium">
          No notifications yet
        </div>

        <div v-else class="overflow-y-auto flex-1">
          <div
            v-for="n in notifications"
            :key="n.id"
            :class="[
              'px-4 py-3 border-b border-gray-100 hover:bg-gray-50 transition-colors',
              !n.is_read && 'bg-gray-50'
            ]"
          >
            <div class="flex items-start gap-2.5">
              <span
                :class="[
                  'w-6 h-6 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5',
                  n.type === 'success' ? 'bg-green-100 text-green-700' :
                  n.type === 'warning' ? 'bg-yellow-100 text-yellow-700' :
                  n.type === 'error' ? 'bg-red-100 text-red-700' :
                  'bg-gray-100 text-gray-700'
                ]"
              >
                {{ typeIcon[n.type] || 'ℹ' }}
              </span>
              <div class="min-w-0 flex-1">
                <p class="text-xs font-bold text-black truncate">{{ n.title }}</p>
                <p class="text-[11px] text-gray-500 mt-0.5 line-clamp-2">{{ n.message }}</p>
                <p class="text-[10px] text-gray-400 mt-1">{{ timeAgo(n.created_at) }}</p>
              </div>
              <span v-if="!n.is_read" class="w-2 h-2 bg-black rounded-full shrink-0 mt-1.5"></span>
            </div>
          </div>
        </div>

        <button
          @click="goToNotifications"
          class="w-full py-2.5 text-xs font-bold text-center uppercase tracking-wider text-gray-600 hover:bg-gray-100 border-t border-gray-200 transition-colors"
        >
          See all notifications
        </button>
      </div>
    </transition>
  </div>
</template>
