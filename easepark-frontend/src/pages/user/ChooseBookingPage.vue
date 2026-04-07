<script setup lang="ts">
import { RouterLink } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import PageHeader from '@/components/PageHeader.vue'
import { Map, List } from 'lucide-vue-next'
</script>

<template>
  <DashboardLayout>
    <PageHeader title="Book Your Spot" subtitle="Choose how you would like to reserve your parking space" />

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-3xl mx-auto mt-4">
      <!-- Book via Map -->
      <RouterLink
        to="/book/map"
        class="group bg-white border-2 border-black p-10 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-1 hover:-translate-y-1 transition-all flex flex-col items-center text-center"
      >
        <div class="w-16 h-16 bg-black text-white flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
          <Map :size="28" />
        </div>
        <h3 class="text-xl font-bold text-black uppercase tracking-tight mb-2">Book via Map</h3>
        <p class="text-sm text-gray-500 font-medium">Find parking lots on an interactive map near your location and reserve directly.</p>
        <span class="mt-6 px-6 py-2 bg-black text-white text-xs font-bold uppercase tracking-widest group-hover:bg-gray-800 transition-colors">Choose Map</span>
      </RouterLink>

      <!-- Book Manually -->
      <RouterLink
        to="/book/list"
        class="group bg-white border-2 border-black p-10 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-1 hover:-translate-y-1 transition-all flex flex-col items-center text-center"
      >
        <div class="w-16 h-16 bg-black text-white flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
          <List :size="28" />
        </div>
        <h3 class="text-xl font-bold text-black uppercase tracking-tight mb-2">Book Manually</h3>
        <p class="text-sm text-gray-500 font-medium">Search lots by name, address, or pin code and reserve from a list.</p>
        <span class="mt-6 px-6 py-2 bg-black text-white text-xs font-bold uppercase tracking-widest group-hover:bg-gray-800 transition-colors">Choose List</span>
      </RouterLink>
    </div>
  </DashboardLayout>
</template>
