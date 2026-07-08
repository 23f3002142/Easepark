<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { CircleParking } from 'lucide-vue-next'

const year = 2026
</script>

<template>
  <!-- ═══════════════════════════════ FOOTER (WHITE) ═══════════════════════════════ -->
  <footer class="bg-white border-t-2 border-black text-black">
    <div class="max-w-7xl mx-auto px-6 lg:px-8 py-20">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-12 lg:gap-16 mb-16">
        <div class="col-span-2 md:col-span-1">
          <RouterLink to="/" class="flex items-center gap-3 mb-6 w-fit">
            <div class="w-8 h-8 bg-black flex items-center justify-center">
              <CircleParking :size="16" class="text-white" />
            </div>
            <span class="font-bold text-xl uppercase tracking-widest">EasePark</span>
          </RouterLink>
          <p class="text-sm text-gray-600 font-medium max-w-xs leading-relaxed">
            High-performance parking infrastructure for the modern city.
          </p>
        </div>

        <div>
          <p class="text-sm font-bold uppercase tracking-widest mb-6">Product</p>
          <ul class="space-y-4">
            <li><RouterLink to="/#features" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">Features</RouterLink></li>
            <li><RouterLink to="/#dashboard" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">Dashboard</RouterLink></li>
            <li><RouterLink to="/#faq" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">FAQ</RouterLink></li>
            <li><RouterLink to="/register" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">Sign up</RouterLink></li>
          </ul>
        </div>

        <div>
          <p class="text-sm font-bold uppercase tracking-widest mb-6">Company</p>
          <ul class="space-y-4">
            <li><RouterLink to="/about" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">About</RouterLink></li>
            <li><a href="https://github.com/23f3002142/Easepark" target="_blank" rel="noopener" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">GitHub</a></li>
            <li><a href="mailto:support.easepark@gmail.com" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">Contact</a></li>
          </ul>
        </div>

        <div>
          <p class="text-sm font-bold uppercase tracking-widest mb-6">Legal</p>
          <ul class="space-y-4">
            <li><RouterLink to="/privacy" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">Privacy Policy</RouterLink></li>
            <li><RouterLink to="/terms" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">Terms of Service</RouterLink></li>
          </ul>
        </div>
      </div>

      <div class="pt-8 border-t-2 border-black flex flex-col md:flex-row items-center justify-between gap-4">
        <p class="text-sm font-bold font-mono text-gray-500">&copy; {{ year }} EASEPARK_SYS.</p>
        <div class="flex items-center gap-3 text-sm font-bold font-mono">
          <span class="w-3 h-3 bg-black rounded-full animate-pulse-soft"></span>
          ALL SYSTEMS NORMAL
        </div>
      </div>
    </div>
  </footer>
</template>
