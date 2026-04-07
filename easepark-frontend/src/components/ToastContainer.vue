<script setup lang="ts">
import { useToast } from '@/composables/useToast'
import { X } from 'lucide-vue-next'

const { toasts } = useToast()

function dismiss(id: number) {
  toasts.value = toasts.value.filter(t => t.id !== id)
}
</script>

<template>
  <teleport to="body">
    <div class="fixed top-6 right-6 z-[9999] flex flex-col gap-3 max-w-sm w-full pointer-events-none">
      <transition-group
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="translate-x-full opacity-0"
        enter-to-class="translate-x-0 opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="translate-x-0 opacity-100"
        leave-to-class="translate-x-full opacity-0"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'pointer-events-auto flex items-start gap-3 p-4 border-2 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] text-sm font-bold',
            toast.type === 'success' ? 'bg-green-50 border-green-600 text-green-800' :
            toast.type === 'error' ? 'bg-red-50 border-red-600 text-red-800' :
            'bg-white border-black text-black'
          ]"
        >
          <span class="flex-1">{{ toast.message }}</span>
          <button @click="dismiss(toast.id)" class="shrink-0 hover:opacity-60">
            <X :size="16" />
          </button>
        </div>
      </transition-group>
    </div>
  </teleport>
</template>
