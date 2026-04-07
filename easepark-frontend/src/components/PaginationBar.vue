<script setup lang="ts">
defineProps<{
  page: number
  totalPages: number
}>()

const emit = defineEmits<{
  (e: 'change', page: number): void
}>()
</script>

<template>
  <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 mt-8">
    <button
      :disabled="page <= 1"
      @click="emit('change', page - 1)"
      class="px-4 py-2 border-2 border-black font-bold text-sm uppercase tracking-wider disabled:opacity-30 disabled:cursor-not-allowed hover:bg-black hover:text-white transition-colors"
    >
      «
    </button>
    <button
      v-for="p in totalPages"
      :key="p"
      @click="emit('change', p)"
      :class="[
        'w-10 h-10 border-2 border-black font-bold text-sm transition-colors',
        p === page ? 'bg-black text-white' : 'hover:bg-black hover:text-white'
      ]"
    >
      {{ p }}
    </button>
    <button
      :disabled="page >= totalPages"
      @click="emit('change', page + 1)"
      class="px-4 py-2 border-2 border-black font-bold text-sm uppercase tracking-wider disabled:opacity-30 disabled:cursor-not-allowed hover:bg-black hover:text-white transition-colors"
    >
      »
    </button>
  </div>
</template>
