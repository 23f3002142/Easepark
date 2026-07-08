<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import { CircleParking, ArrowLeft } from 'lucide-vue-next'
import SiteFooter from './SiteFooter.vue'

const authStore = useAuthStore()
const isLoggedIn = computed(() => authStore.isAuthenticated)
</script>

<template>
  <div class="bg-white min-h-screen flex flex-col text-gray-900 font-sans selection:bg-black selection:text-white">
    <!-- ─── Simple top bar ─── -->
    <nav class="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b-2 border-black">
      <div class="max-w-7xl mx-auto px-6 lg:px-8 py-4 flex items-center justify-between">
        <RouterLink to="/" class="flex items-center gap-2.5 group">
          <div class="w-8 h-8 bg-black text-white flex items-center justify-center rounded-md">
            <CircleParking :size="18" />
          </div>
          <span class="font-bold tracking-tight text-black text-lg">EasePark</span>
        </RouterLink>

        <div class="flex items-center gap-4">
          <RouterLink
            to="/"
            class="hidden sm:inline-flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-black transition-colors"
          >
            <ArrowLeft :size="16" /> Back to home
          </RouterLink>
          <template v-if="!isLoggedIn">
            <RouterLink
              to="/register"
              class="px-5 py-2.5 bg-black text-white text-sm font-medium rounded-md hover:bg-gray-800 transition-all duration-300"
            >
              Get Started
            </RouterLink>
          </template>
          <template v-else>
            <RouterLink
              to="/dashboard"
              class="px-5 py-2.5 bg-black text-white text-sm font-medium rounded-md hover:bg-gray-800 transition-all duration-300"
            >
              Dashboard
            </RouterLink>
          </template>
        </div>
      </div>
    </nav>

    <!-- ─── Page content ─── -->
    <main class="flex-1">
      <slot />
    </main>

    <SiteFooter />
  </div>
</template>
