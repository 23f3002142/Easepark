<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  label: string
  value: string | number
  prefix?: string
  icon?: Component
}>()
</script>

<template>
  <div class="bg-white border-2 border-black p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
    <p class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-2">{{ label }}</p>
    <p class="text-3xl font-bold text-black">{{ prefix || '' }}{{ value }}</p>
  </div>
</template>
