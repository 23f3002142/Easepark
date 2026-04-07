<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import {
  Car, MapPin, Shield, Zap, CreditCard, BarChart3,
  Search, CircleParking,
  Menu, X,
  ArrowRight, CheckCircle2, Map, CalendarCheck, Clock,
  Settings, Star
} from 'lucide-vue-next'

const authStore = useAuthStore()
const isLoggedIn = computed(() => authStore.isAuthenticated)
const mobileMenuOpen = ref(false)
const scrolled = ref(false)

const handleScroll = () => {
  scrolled.value = window.scrollY > 20
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    window.addEventListener('scroll', handleScroll)
  }
})

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('scroll', handleScroll)
  }
})

const features = [
  {
    icon: Map,
    title: 'Live Map View',
    description: 'See every available spot on an interactive map. No more circling blocks — just open, find, and go.',
  },
  {
    icon: Zap,
    title: 'Instant Booking',
    description: 'Reserve your spot in under 10 seconds. OTP verification keeps your booking secure.',
  },
  {
    icon: CreditCard,
    title: 'Seamless Payments',
    description: 'Pay only for the time you park. Razorpay-powered checkout with automatic receipts.',
  },
  {
    icon: BarChart3,
    title: 'Smart Analytics',
    description: 'Track your parking history, spending patterns, and duration trends on a personal dashboard.',
  },
  {
    icon: Shield,
    title: 'Secure by Default',
    description: 'JWT authentication, email OTP verification, and encrypted payments protect every transaction.',
  },
  {
    icon: Settings,
    title: 'Admin Control Center',
    description: 'Manage lots, set pricing, monitor occupancy, and track revenue — all from one dashboard.',
  },
]

const steps = [
  {
    number: '01',
    icon: Search,
    title: 'Search location',
    description: 'Enter your pin code or browse the live map.',
  },
  {
    number: '02',
    icon: CalendarCheck,
    title: 'Book a spot',
    description: 'Pick an available slot and confirm with OTP.',
  },
  {
    number: '03',
    icon: Car,
    title: 'Park & go',
    description: 'Drive in, park, and pay only for time used.',
  },
]

const dashboardStats = [
  { label: 'Active Bookings', value: '3', icon: CircleParking },
  { label: 'This Month', value: '12', icon: CalendarCheck },
  { label: 'Total Spent', value: '2,450', prefix: '₹', icon: CreditCard },
  { label: 'Hours Saved', value: '48+', icon: Clock },
]

const testimonials = [
  {
    name: 'Arjun Mehta',
    role: 'Daily Commuter, Bangalore',
    text: 'I used to spend 20 minutes every morning finding parking. EasePark cut that to zero. I just book on my way and walk straight in.',
    rating: 5,
  },
  {
    name: 'Priya Sharma',
    role: 'Lot Manager, Delhi',
    text: 'The admin dashboard gives me complete control. I can see occupancy in real-time, adjust pricing, and track revenue — all in one place.',
    rating: 5,
  },
  {
    name: 'Rahul Verma',
    role: 'Weekend Driver, Mumbai',
    text: 'The map view is a game-changer. I can see exactly which lots have spots before I even leave home. No more uncertainty.',
    rating: 5,
  },
]
</script>

<template>
  <div class="bg-white min-h-screen text-gray-900 font-sans selection:bg-black selection:text-white">
    <!-- ═══════════════════════════════ NAVBAR ═══════════════════════════════ -->
    <nav
      :class="[
        'fixed top-0 left-0 right-0 z-50 transition-all duration-300 border-b',
        scrolled ? 'bg-white/90 backdrop-blur-md border-gray-200 py-3 shadow-sm' : 'bg-white border-transparent py-5'
      ]"
    >
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <div class="flex items-center justify-between">
          <!-- Logo -->
          <RouterLink to="/" class="flex items-center gap-2.5 group">
            <div class="w-8 h-8 bg-black text-white flex items-center justify-center rounded-md">
              <CircleParking :size="18" />
            </div>
            <span class="font-bold tracking-tight text-black text-lg">
              EasePark
            </span>
          </RouterLink>

          <!-- Desktop Nav -->
          <div class="hidden lg:flex items-center gap-8">
            <a
              v-for="link in [
                { label: 'Features', href: '#features' },
                { label: 'How It Works', href: '#how-it-works' },
                { label: 'Dashboard', href: '#dashboard' },
                { label: 'Contact', href: '#contact' },
              ]"
              :key="link.href"
              :href="link.href"
              class="text-sm font-medium text-gray-500 hover:text-black transition-colors duration-200"
            >
              {{ link.label }}
            </a>
          </div>

          <!-- Auth Buttons (Desktop) -->
          <div class="hidden lg:flex items-center gap-4">
            <template v-if="!isLoggedIn">
              <RouterLink
                to="/login"
                class="text-sm font-medium text-black hover:text-gray-600 transition-colors duration-200"
              >
                Log in
              </RouterLink>
              <RouterLink
                to="/register"
                class="px-5 py-2.5 bg-black text-white text-sm font-medium rounded-md hover:bg-gray-800 transition-all duration-300"
              >
                Get Started
              </RouterLink>
            </template>
            <template v-else>
              <RouterLink
                to="/"
                class="px-5 py-2.5 bg-black text-white text-sm font-medium rounded-md hover:bg-gray-800 transition-all duration-300"
              >
                Dashboard
              </RouterLink>
            </template>
          </div>

          <!-- Mobile Menu Button -->
          <button
            class="lg:hidden p-2 text-black"
            @click="mobileMenuOpen = !mobileMenuOpen"
          >
            <X v-if="mobileMenuOpen" :size="24" />
            <Menu v-else :size="24" />
          </button>
        </div>

        <!-- Mobile Menu -->
        <transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 -translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2"
        >
          <div v-if="mobileMenuOpen" class="lg:hidden absolute top-full left-0 right-0 bg-white border-b border-gray-200 py-4 px-6 shadow-xl space-y-4">
            <a v-for="link in ['Features', 'How It Works', 'Dashboard', 'Contact']" :key="link" :href="`#${link.toLowerCase().replace(/ /g, '-')}`" @click="mobileMenuOpen = false" class="block text-gray-900 font-medium hover:text-black text-base transition-colors">
              {{ link }}
            </a>
            <hr class="border-gray-100" />
            <div class="flex flex-col gap-3 pt-2">
              <template v-if="!isLoggedIn">
                <RouterLink to="/login" @click="mobileMenuOpen = false" class="text-black font-medium hover:text-gray-600 transition-colors">Log in</RouterLink>
                <RouterLink to="/register" @click="mobileMenuOpen = false" class="inline-flex justify-center px-4 py-3 bg-black text-white text-base font-medium rounded-md">Get Started</RouterLink>
              </template>
            </div>
          </div>
        </transition>
      </div>
    </nav>

    <!-- ═══════════════════════════════ HERO (BLACK) ═══════════════════════════════ -->
    <section class="relative pt-32 pb-20 lg:pt-48 lg:pb-32 bg-black text-white overflow-hidden">
      <!-- Minimal grid overlay -->
      <div class="absolute inset-0 opacity-[0.1]" style="background-image: linear-gradient(to right, #ffffff 1px, transparent 1px), linear-gradient(to bottom, #ffffff 1px, transparent 1px); background-size: 64px 64px;"></div>
      
      <div class="relative z-10 max-w-7xl mx-auto px-6 lg:px-8">
        <div class="grid lg:grid-cols-2 gap-16 lg:gap-24 items-center">
          
          <!-- Left — Copy -->
          <div class="animate-fade-up max-w-2xl">
            <div class="inline-flex items-center gap-2 px-3 py-1.5 bg-white/10 border border-white/20 rounded-full mb-8">
              <div class="w-2 h-2 bg-white rounded-full animate-pulse-soft"></div>
              <span class="text-white text-xs font-semibold uppercase tracking-widest">EasePark 2.0</span>
            </div>

            <h1 class="text-5xl lg:text-[5rem] font-bold tracking-tighter text-white leading-[1.0] mb-8">
              Stop circling.<br />
              <span class="text-gray-400">Start parking.</span>
            </h1>

            <p class="text-lg md:text-xl text-gray-300 mb-10 leading-relaxed font-light max-w-lg">
              The high-contrast, high-performance platform to find, book, and manage your parking across the city seamlessly.
            </p>

            <div class="flex flex-col sm:flex-row gap-4">
              <RouterLink
                to="/register"
                class="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-black font-bold rounded-none hover:bg-gray-200 transition-all duration-200"
              >
                Find Parking
                <ArrowRight :size="18" />
              </RouterLink>
              <a
                href="#how-it-works"
                class="inline-flex items-center justify-center gap-2 px-8 py-4 bg-transparent text-white border-2 border-white hover:bg-white hover:text-black font-bold rounded-none transition-all duration-200"
              >
                View Demo
              </a>
            </div>
          </div>

          <!-- Right — Stark Visual Mockup -->
          <div class="hidden lg:block animate-fade-up animate-fade-up-delay-2 relative">
            <!-- Brutalist floating card -->
            <div class="bg-black border-2 border-white p-6 shadow-[12px_12px_0px_0px_rgba(255,255,255,1)] relative z-10">
              <div class="flex items-center justify-between mb-8 pb-4 border-b-2 border-white/20">
                <div class="flex items-center gap-3">
                  <MapPin :size="20" class="text-white" />
                  <p class="text-base font-bold text-white uppercase tracking-wider">Live Radar</p>
                </div>
                <div class="flex gap-1.5">
                  <div class="w-3 h-3 border-2 border-white rounded-full"></div>
                  <div class="w-3 h-3 bg-white rounded-full"></div>
                </div>
              </div>

              <div class="space-y-4">
                <div v-for="(lot, i) in [
                  { name: 'Sector 17 Plaza', spots: 5, total: 25, price: 25 },
                  { name: 'MG Road Central', spots: 12, total: 40, price: 30 },
                  { name: 'City Mall Base', spots: 23, total: 60, price: 20 },
                ]" :key="i" class="bg-black border border-white/20 p-4 hover:border-white transition-all cursor-pointer flex justify-between items-center group">
                  <div>
                    <p class="text-white font-bold group-hover:underline">{{ lot.name }}</p>
                    <p class="text-sm text-gray-400 mt-1 font-mono">{{ lot.spots }}/{{ lot.total }} FREE</p>
                  </div>
                  <div class="text-right">
                    <p class="text-white font-bold font-mono">₹{{ lot.price }}/H</p>
                    <div class="w-20 h-2 bg-white/20 mt-2">
                      <div class="h-full bg-white" :style="{ width: `${(lot.spots / lot.total) * 100}%` }"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════ TRUST BAR (WHITE) ═══════════════════════════════ -->
    <section class="border-b-2 border-black bg-white">
      <div class="max-w-7xl mx-auto px-6 lg:px-8 py-12">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 divide-x-2 divide-gray-200">
          <div v-for="stat in [
            { v: '25+', l: 'Locations' },
            { v: '500+', l: 'Spots' },
            { v: '99.9%', l: 'Uptime' },
            { v: '<10s', l: 'Booking' }
          ]" :key="stat.l" class="text-center px-4">
            <p class="text-4xl lg:text-5xl font-bold tracking-tighter text-black">{{ stat.v }}</p>
            <p class="text-sm text-gray-500 uppercase tracking-widest mt-2 font-semibold">{{ stat.l }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════ FEATURES (WHITE) ═══════════════════════════════ -->
    <section id="features" class="py-32 bg-white">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <div class="max-w-3xl mb-20">
          <h2 class="text-4xl md:text-5xl font-bold tracking-tighter text-black mb-6">Engineered for speed.</h2>
          <p class="text-xl text-gray-600 font-light leading-relaxed">A strictly uncompromised toolset designed to get you parked and moving without friction.</p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div
            v-for="feature in features"
            :key="feature.title"
            class="bg-white border-2 border-black p-8 lg:p-10 hover:bg-black hover:text-white transition-colors duration-300 group shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-y-1 hover:translate-x-1"
          >
            <component :is="feature.icon" :size="32" class="text-black mb-6 group-hover:text-white transition-colors" />
            <h3 class="text-xl font-bold mb-3 tracking-tight group-hover:text-white">{{ feature.title }}</h3>
            <p class="text-sm text-gray-600 leading-relaxed font-medium group-hover:text-gray-300">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════ HOW IT WORKS (BLACK) ═══════════════════════════════ -->
    <section id="how-it-works" class="py-32 bg-black text-white border-y-2 border-black">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <div class="max-w-2xl mb-20 text-center mx-auto">
          <h2 class="text-4xl md:text-5xl font-bold tracking-tighter mb-6">Zero friction flow.</h2>
          <p class="text-xl text-gray-400 font-light">Three stages from ignition to parked.</p>
        </div>

        <div class="grid md:grid-cols-3 gap-12 relative">
          <!-- Connector -->
          <div class="hidden md:block absolute top-10 left-[16.6%] right-[16.6%] h-px border-t-2 border-dashed border-white/30 z-0"></div>

          <div
            v-for="step in steps"
            :key="step.number"
            class="relative z-10 text-center"
          >
            <div class="w-20 h-20 mx-auto bg-black border-2 border-white flex items-center justify-center mb-8 text-white relative shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]">
              <component :is="step.icon" :size="32" />
              <div class="absolute -top-3 -right-3 bg-white text-black font-bold font-mono text-xs px-2 py-1">{{ step.number }}</div>
            </div>
            <h3 class="text-2xl font-bold mb-3 tracking-tight">{{ step.title }}</h3>
            <p class="text-base text-gray-400 font-light max-w-xs mx-auto">{{ step.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════ DASHBOARD PREVIEW (WHITE) ═══════════════════════════════ -->
    <section id="dashboard" class="py-32 bg-white">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <div class="grid lg:grid-cols-2 gap-20 items-center">
          <div>
            <h2 class="text-4xl md:text-5xl font-bold tracking-tighter text-black mb-6">Total visibility.</h2>
            <p class="text-xl text-gray-600 font-light mb-8 leading-relaxed">
              Track active bookings, review history, and manage your receipts through a completely minimalist control panel.
            </p>
            <ul class="space-y-6 mb-12">
              <li v-for="item in ['Real-time status tracking', 'Downloadable digital receipts', 'Usage duration analytics']" :key="item" class="flex items-center gap-4">
                <div class="w-6 h-6 bg-black flex items-center justify-center shrink-0">
                  <CheckCircle2 :size="14" class="text-white" />
                </div>
                <span class="text-lg text-gray-800 font-medium">{{ item }}</span>
              </li>
            </ul>
            <RouterLink
              to="/register"
              class="inline-flex items-center gap-2 text-base font-bold text-black border-b-2 border-black pb-1 hover:text-gray-500 hover:border-gray-500 transition-colors uppercase tracking-widest"
            >
              Explore Dashboard <ArrowRight :size="18" />
            </RouterLink>
          </div>

          <!-- Mockup -->
          <div class="bg-gray-100 border-2 border-black p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            <div class="grid grid-cols-2 gap-4 mb-8">
              <div v-for="stat in dashboardStats" :key="stat.label" class="bg-white border-2 border-black p-5">
                <p class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-2">{{ stat.label }}</p>
                <p class="text-3xl font-bold text-black">{{ stat.prefix || '' }}{{ stat.value }}</p>
              </div>
            </div>

            <div class="bg-white border-2 border-black p-6">
              <div class="flex justify-between items-center mb-6 border-b-2 border-black pb-4">
                <p class="font-bold text-black uppercase tracking-wider">Activity</p>
                <p class="text-sm font-mono font-bold">7 DAYS</p>
              </div>
              <div class="flex items-end gap-3 h-24">
                <div v-for="(h, i) in [40, 65, 45, 80, 55, 90, 70]" :key="i" class="flex-1 bg-gray-200 relative group cursor-crosshair">
                  <div class="absolute bottom-0 left-0 right-0 bg-black transition-all group-hover:bg-gray-800" :style="{ height: `${h}%` }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════ ADMIN SECTION (BLACK) ═══════════════════════════════ -->
    <section class="py-32 bg-black text-white border-y-2 border-black">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <div class="grid lg:grid-cols-2 gap-20 items-center">
          
          <div class="order-2 lg:order-1 bg-black border-2 border-white p-8 shadow-[-8px_8px_0px_0px_rgba(255,255,255,1)]">
            <div class="flex items-center justify-between mb-8 pb-4 border-b-2 border-white/20">
              <p class="text-lg font-bold text-white uppercase tracking-widest">Ops Terminal</p>
              <div class="px-2 py-1 bg-white text-black text-xs font-bold font-mono">LIVE</div>
            </div>
            
            <div class="space-y-6">
              <div v-for="lot in [
                { id: 'SYS_L01', occ: 70, rev: '12.4k' },
                { id: 'SYS_L02', occ: 80, rev: '8.6k' },
                { id: 'SYS_L03', occ: 38, rev: '15.2k' },
              ]" :key="lot.id" class="flex items-center justify-between">
                <span class="text-sm font-bold font-mono text-white">{{ lot.id }}</span>
                <div class="flex-1 mx-6 h-px border-t border-dashed border-white/40"></div>
                <div class="flex gap-6 items-center">
                  <span class="text-sm font-mono">{{ lot.occ }}% FULL</span>
                  <span class="text-sm font-bold bg-white text-black px-2 py-0.5">₹{{ lot.rev }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="order-1 lg:order-2">
            <h2 class="text-4xl md:text-5xl font-bold tracking-tighter text-white mb-6">Absolute control.</h2>
            <p class="text-xl text-gray-400 font-light leading-relaxed">
              Administrative tools built for scale. Dictate lot capacity, enforce pricing models, and monitor live revenue streams from a centralized command center.
            </p>
          </div>
          
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════ TESTIMONIALS (WHITE) ═══════════════════════════════ -->
    <section class="py-32 bg-white">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <h2 class="text-4xl md:text-5xl font-bold tracking-tighter text-black mb-16 text-center">System Feedback.</h2>
        <div class="grid md:grid-cols-3 gap-8">
          <div
            v-for="testimonial in testimonials"
            :key="testimonial.name"
            class="bg-white border-2 border-black p-8 relative"
          >
            <div class="absolute -top-4 -left-4 w-8 h-8 bg-black text-white flex items-center justify-center font-bold text-xl">"</div>
            <div class="flex gap-1 mb-6 mt-2">
              <Star v-for="n in testimonial.rating" :key="n" :size="16" class="text-black fill-black" />
            </div>
            <p class="text-lg text-gray-800 font-medium mb-8">"{{ testimonial.text }}"</p>
            <div class="pt-6 border-t-2 border-black">
              <p class="text-base font-bold text-black uppercase tracking-wider">{{ testimonial.name }}</p>
              <p class="text-sm text-gray-500 font-mono mt-1">{{ testimonial.role }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════ FINAL CTA (BLACK) ═══════════════════════════════ -->
    <section class="py-40 bg-black text-white border-t-2 border-black text-center relative">
      <!-- Grid background -->
      <div class="absolute inset-0 opacity-20" style="background-image: radial-gradient(circle, #ffffff 2px, transparent 2px); background-size: 40px 40px;"></div>
      
      <div class="relative z-10 max-w-3xl mx-auto px-6">
        <h2 class="text-5xl md:text-7xl font-bold tracking-tighter mb-8 leading-tight">
          Ready to deploy?
        </h2>
        <p class="text-xl text-gray-400 font-light mb-12 max-w-lg mx-auto">
          Create an account and initialize your smart parking workflow in seconds.
        </p>
        <RouterLink
          to="/register"
          class="inline-flex items-center justify-center px-10 py-5 bg-white text-black font-bold text-lg hover:bg-gray-200 transition-colors uppercase tracking-widest shadow-[8px_8px_0px_0px_rgba(100,100,100,1)] hover:shadow-none hover:translate-y-2 hover:translate-x-2"
        >
          Initialize Account
        </RouterLink>
      </div>
    </section>

    <!-- ═══════════════════════════════ FOOTER (WHITE) ═══════════════════════════════ -->
    <footer class="bg-white border-t-2 border-black text-black">
      <div class="max-w-7xl mx-auto px-6 lg:px-8 py-20">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-12 lg:gap-16 mb-16">
          <div class="col-span-2 md:col-span-1">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-8 h-8 bg-black flex items-center justify-center">
                <CircleParking :size="16" class="text-white" />
              </div>
              <span class="font-bold text-xl uppercase tracking-widest">EasePark</span>
            </div>
            <p class="text-sm text-gray-600 font-medium max-w-xs leading-relaxed">
              High-performance parking infrastructure for the modern city.
            </p>
          </div>

          <div>
            <p class="text-sm font-bold uppercase tracking-widest mb-6">Product</p>
            <ul class="space-y-4">
              <li><a href="#features" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">Features</a></li>
              <li><a href="#dashboard" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">Dashboard</a></li>
              <li><RouterLink to="/register" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">Sign up</RouterLink></li>
            </ul>
          </div>

          <div>
            <p class="text-sm font-bold uppercase tracking-widest mb-6">Connect</p>
            <ul class="space-y-4">
              <li><a href="#" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">Twitter / X</a></li>
              <li><a href="#" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">GitHub</a></li>
              <li><a href="#" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">LinkedIn</a></li>
            </ul>
          </div>

          <div>
            <p class="text-sm font-bold uppercase tracking-widest mb-6">Legal</p>
            <ul class="space-y-4">
              <li><a href="#" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">Privacy Policy</a></li>
              <li><a href="#" class="text-sm font-medium text-gray-600 hover:text-black transition-colors">Terms of Service</a></li>
            </ul>
          </div>
        </div>

        <div class="pt-8 border-t-2 border-black flex flex-col md:flex-row items-center justify-between gap-4">
          <p class="text-sm font-bold font-mono text-gray-500">&copy; 2025 EASEPARK_SYS.</p>
          <div class="flex items-center gap-3 text-sm font-bold font-mono">
            <span class="w-3 h-3 bg-black rounded-full animate-pulse-soft"></span>
            ALL SYSTEMS NORMAL
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>
