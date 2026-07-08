<script setup lang="ts">
import { RouterLink } from 'vue-router'
import PublicPageLayout from '@/components/PublicPageLayout.vue'
import { ArrowRight, Target, Zap, ShieldCheck, MapPin } from 'lucide-vue-next'

const values = [
  {
    icon: Zap,
    title: 'Speed first',
    description: 'Every interaction is engineered to be fast. Booking a spot should take seconds, not minutes.',
  },
  {
    icon: ShieldCheck,
    title: 'Secure by default',
    description: 'JWT authentication, OTP verification, and Razorpay-secured payments protect every transaction.',
  },
  {
    icon: Target,
    title: 'No friction',
    description: 'A ruthlessly minimal interface. We remove steps instead of adding them.',
  },
  {
    icon: MapPin,
    title: 'Real-time truth',
    description: 'Live occupancy on an interactive map means you always know where the open spots are.',
  },
]
</script>

<template>
  <PublicPageLayout>
    <!-- Hero -->
    <section class="bg-black text-white border-b-2 border-black">
      <div class="max-w-7xl mx-auto px-6 lg:px-8 py-24 lg:py-32">
        <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-6">About EasePark</p>
        <h1 class="text-4xl md:text-6xl font-bold tracking-tighter leading-[1.05] max-w-3xl">
          We are killing the<br />parking hunt.
        </h1>
        <p class="text-lg md:text-xl text-gray-300 font-light leading-relaxed mt-8 max-w-2xl">
          EasePark is a smart parking platform that lets drivers find, reserve, and pay for parking spots
          in real time — while giving lot operators a live command center to manage capacity, pricing, and revenue.
        </p>
      </div>
    </section>

    <!-- Mission -->
    <section class="bg-white py-24">
      <div class="max-w-7xl mx-auto px-6 lg:px-8 grid lg:grid-cols-2 gap-16 items-start">
        <h2 class="text-3xl md:text-4xl font-bold tracking-tighter text-black">Our mission.</h2>
        <div class="space-y-6 text-lg text-gray-700 font-light leading-relaxed">
          <p>
            Drivers waste countless hours every year circling blocks looking for a place to park. That wasted time
            burns fuel, adds traffic, and starts every trip with frustration.
          </p>
          <p>
            We built EasePark to make parking a solved problem: open the app, see what's available near you,
            reserve it, and drive straight in. No circling, no guessing, no cash at the gate.
          </p>
          <p>
            For the businesses that run parking lots, EasePark turns guesswork into data — real-time occupancy,
            flexible pricing, and transparent revenue tracking from a single dashboard.
          </p>
        </div>
      </div>
    </section>

    <!-- Values -->
    <section class="bg-white pb-24">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <h2 class="text-3xl md:text-4xl font-bold tracking-tighter text-black mb-12">What we stand for.</h2>
        <div class="grid sm:grid-cols-2 gap-8">
          <div
            v-for="value in values"
            :key="value.title"
            class="bg-white border-2 border-black p-8 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]"
          >
            <component :is="value.icon" :size="32" class="text-black mb-6" />
            <h3 class="text-xl font-bold mb-3 tracking-tight">{{ value.title }}</h3>
            <p class="text-sm text-gray-600 leading-relaxed font-medium">{{ value.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-black text-white border-t-2 border-black py-24 text-center">
      <div class="max-w-2xl mx-auto px-6">
        <h2 class="text-3xl md:text-5xl font-bold tracking-tighter mb-6">Park smarter today.</h2>
        <p class="text-lg text-gray-400 font-light mb-10">
          Create a free account and book your first spot in seconds.
        </p>
        <RouterLink
          to="/register"
          class="inline-flex items-center gap-2 px-8 py-4 bg-white text-black font-bold hover:bg-gray-200 transition-colors uppercase tracking-widest"
        >
          Get Started <ArrowRight :size="18" />
        </RouterLink>
      </div>
    </section>
  </PublicPageLayout>
</template>
