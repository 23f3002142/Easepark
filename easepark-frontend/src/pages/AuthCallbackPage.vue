<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

onMounted(async () => {
  const token = route.query.token as string
  if (token) {
    authStore.setToken(token)
    await authStore.fetchProfile()
    if (authStore.isAdmin) {
      router.push('/admin')
    } else {
      router.push('/dashboard')
    }
  } else {
    router.push('/login')
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-black">
    <div class="text-center text-white">
      <div class="animate-spin w-8 h-8 border-4 border-white/30 border-t-white mx-auto mb-4"></div>
      <p class="text-lg font-bold uppercase tracking-widest">Signing you in...</p>
    </div>
  </div>
</template>
