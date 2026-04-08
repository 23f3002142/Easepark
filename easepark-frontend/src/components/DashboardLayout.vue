<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import {
  CircleParking, Menu, X, LayoutDashboard, Car, Clock,
  BarChart3, User, Settings, Users, Search, LogOut, ChevronDown, Bell
} from 'lucide-vue-next'
import NotificationBell from '@/components/NotificationBell.vue'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const mobileOpen = ref(false)
const profileOpen = ref(false)

const isAdmin = computed(() => authStore.isAdmin)

const userLinks = [
  { label: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
  { label: 'Book Spot', to: '/book', icon: Car },
  { label: 'My Bookings', to: '/bookings', icon: Clock },
  { label: 'Summary', to: '/summary', icon: BarChart3 },
]

const adminLinks = [
  { label: 'Dashboard', to: '/admin', icon: LayoutDashboard },
  { label: 'Users', to: '/admin/users', icon: Users },
  { label: 'Search', to: '/admin/search', icon: Search },
  { label: 'Summary', to: '/admin/summary', icon: BarChart3 },
]

const links = computed(() => isAdmin.value ? adminLinks : userLinks)

function isActive(to: string) {
  return route.path === to || route.path.startsWith(to + '/')
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- Navbar -->
    <nav class="fixed top-0 left-0 right-0 z-50 bg-white border-b-2 border-black">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <RouterLink to="/" class="flex items-center gap-2.5">
            <div class="w-8 h-8 bg-black text-white flex items-center justify-center rounded-md">
              <CircleParking :size="18" />
            </div>
            <span class="font-bold tracking-tight text-black text-lg">EasePark</span>
          </RouterLink>

          <!-- Desktop Nav -->
          <div class="hidden lg:flex items-center gap-1">
            <RouterLink
              v-for="link in links"
              :key="link.to"
              :to="link.to"
              :class="[
                'px-4 py-2 text-sm font-bold uppercase tracking-wider transition-all duration-200',
                isActive(link.to)
                  ? 'bg-black text-white'
                  : 'text-gray-600 hover:text-black hover:bg-gray-100'
              ]"
            >
              {{ link.label }}
            </RouterLink>
          </div>

          <!-- Desktop Profile -->
          <div class="hidden lg:flex items-center gap-4">
            <NotificationBell v-if="!isAdmin" />
            <div class="text-right mr-2">
              <p class="text-sm font-bold text-black">{{ authStore.user?.username }}</p>
              <p class="text-xs text-gray-500 font-mono">{{ authStore.user?.email }}</p>
            </div>
            <div class="relative">
              <button
                @click="profileOpen = !profileOpen"
                class="px-4 py-2 bg-black text-white text-sm font-bold uppercase tracking-wider hover:bg-gray-800 transition-colors flex items-center gap-2"
              >
                Profile
                <ChevronDown :size="14" />
              </button>
              <transition
                enter-active-class="transition duration-100 ease-out"
                enter-from-class="opacity-0 scale-95"
                enter-to-class="opacity-100 scale-100"
                leave-active-class="transition duration-75 ease-in"
                leave-from-class="opacity-100 scale-100"
                leave-to-class="opacity-0 scale-95"
              >
                <div v-if="profileOpen" class="absolute right-0 mt-2 w-48 bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] z-50">
                  <RouterLink
                    :to="isAdmin ? '/admin/profile' : '/profile'"
                    @click="profileOpen = false"
                    class="block px-4 py-3 text-sm font-bold hover:bg-gray-100 border-b border-gray-200"
                  >
                    <User :size="14" class="inline mr-2" />View Profile
                  </RouterLink>
                  <RouterLink
                    :to="isAdmin ? '/admin/profile/edit' : '/profile/edit'"
                    @click="profileOpen = false"
                    class="block px-4 py-3 text-sm font-bold hover:bg-gray-100 border-b border-gray-200"
                  >
                    <Settings :size="14" class="inline mr-2" />Edit Profile
                  </RouterLink>
                  <button
                    @click="logout"
                    class="w-full text-left px-4 py-3 text-sm font-bold text-red-600 hover:bg-red-50"
                  >
                    <LogOut :size="14" class="inline mr-2" />Logout
                  </button>
                </div>
              </transition>
            </div>
          </div>

          <!-- Mobile Menu -->
          <button class="lg:hidden p-2 text-black" @click="mobileOpen = !mobileOpen">
            <X v-if="mobileOpen" :size="24" />
            <Menu v-else :size="24" />
          </button>
        </div>

        <!-- Mobile Dropdown -->
        <transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 -translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2"
        >
          <div v-if="mobileOpen" class="lg:hidden absolute top-full left-0 right-0 bg-white border-b-2 border-black shadow-xl px-6 py-4 space-y-2">
            <RouterLink
              v-for="link in links"
              :key="link.to"
              :to="link.to"
              @click="mobileOpen = false"
              :class="[
                'block px-4 py-3 text-base font-bold uppercase tracking-wider',
                isActive(link.to) ? 'bg-black text-white' : 'text-gray-800 hover:bg-gray-100'
              ]"
            >
              {{ link.label }}
            </RouterLink>
            <hr class="border-gray-200 my-2" />
            <div class="px-4 py-2">
              <p class="font-bold text-black">{{ authStore.user?.username }}</p>
              <p class="text-sm text-gray-500 font-mono">{{ authStore.user?.email }}</p>
            </div>
            <RouterLink :to="isAdmin ? '/admin/profile' : '/profile'" @click="mobileOpen = false" class="block px-4 py-2 font-bold text-gray-800 hover:bg-gray-100">View Profile</RouterLink>
            <RouterLink :to="isAdmin ? '/admin/profile/edit' : '/profile/edit'" @click="mobileOpen = false" class="block px-4 py-2 font-bold text-gray-800 hover:bg-gray-100">Edit Profile</RouterLink>
            <RouterLink v-if="!isAdmin" to="/notifications" @click="mobileOpen = false" class="block px-4 py-2 font-bold text-gray-800 hover:bg-gray-100"><Bell :size="14" class="inline mr-2" />Notifications</RouterLink>
            <button @click="logout" class="w-full text-left px-4 py-2 font-bold text-red-600 hover:bg-red-50">Logout</button>
          </div>
        </transition>
      </div>
    </nav>

    <!-- Content -->
    <main class="pt-20 pb-16">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <slot />
      </div>
    </main>
  </div>
</template>
