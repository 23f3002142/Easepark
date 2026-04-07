<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <div class="mb-8">
    <h1 class="text-3xl md:text-4xl font-bold tracking-tighter text-black">{{ title }}</h1>
    <p v-if="subtitle" class="text-lg text-gray-500 font-medium mt-2">{{ subtitle }}</p>
  </div>
</template>
