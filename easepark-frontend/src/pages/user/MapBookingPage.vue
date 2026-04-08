<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
// leaflet-routing-machine is loaded dynamically on first route request
let routingLoaded = false
import { getAllLots, getNearbyLots, reserveSpot, type NearbyLot } from '@/api/user.api'
import { useToast } from '@/composables/useToast'

// Fix Leaflet default icon paths
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const router = useRouter()
const toast = useToast()

const mapContainer = ref<HTMLDivElement | null>(null)
const loading = ref(true)
const locating = ref(true)
const error = ref('')

// User location
const userLat = ref<number | null>(null)
const userLng = ref<number | null>(null)
const locationMode = ref<'gps' | 'manual' | null>(null)
const showLocationPrompt = ref(true)

// Nearby lots panel
const nearbyLots = ref<NearbyLot[]>([])
const nearbyLoading = ref(false)
const showNearbyPanel = ref(false)
const nearbyCollapsed = ref(false)

// Route info
const routeDistance = ref('')
const routeTime = ref('')
const routeTarget = ref<string | null>(null)
const showRouteInfo = ref(false)
const routeCalculating = ref(false)

// Reserve modal
const showModal = ref(false)
const selectedLot = ref<any>(null)
const vehicleNumber = ref('')
const reserveLoading = ref(false)
const reserveError = ref('')

const DEFAULT_LAT = 23.2599
const DEFAULT_LNG = 77.4126

// Map and layer refs (not reactive to avoid proxy overhead)
let map: L.Map | null = null
let userMarker: L.Marker | null = null
let routingControl: any = null
let lotMarkers: L.Marker[] = []

const userIcon = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

const parkingIcon = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

onMounted(() => {
  if (!mapContainer.value) return
  map = L.map(mapContainer.value).setView([DEFAULT_LAT, DEFAULT_LNG], 13)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)
  loading.value = false
})

onUnmounted(() => {
  if (map) { map.remove(); map = null }
})

// ─── Location Methods ───
function useGpsLocation() {
  showLocationPrompt.value = false
  locating.value = true
  locationMode.value = 'gps'

  if (!navigator.geolocation) {
    toast.error('Geolocation not supported by your browser')
    locating.value = false
    fallbackInit()
    return
  }

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      setUserLocation(pos.coords.latitude, pos.coords.longitude)
      locating.value = false
    },
    () => {
      toast.error('Could not access your location. Please pin manually.')
      locationMode.value = 'manual'
      enableManualPin()
      locating.value = false
    },
    { enableHighAccuracy: true, timeout: 10000 }
  )
}

function useManualPin() {
  showLocationPrompt.value = false
  locationMode.value = 'manual'
  locating.value = false
  enableManualPin()
}

function enableManualPin() {
  if (!map) return
  toast.info('Tap on the map to set your location')
  map.once('click', (e: L.LeafletMouseEvent) => {
    setUserLocation(e.latlng.lat, e.latlng.lng)
  })
}

function setUserLocation(lat: number, lng: number) {
  userLat.value = lat
  userLng.value = lng

  if (!map) return

  // Place/move user marker
  if (userMarker) {
    userMarker.setLatLng([lat, lng])
  } else {
    userMarker = L.marker([lat, lng], { icon: userIcon, zIndexOffset: 1000 })
      .addTo(map)
      .bindPopup('<b style="font-size:13px;">📍 You are here</b>')
      .openPopup()
  }

  map.setView([lat, lng], 14)

  // Load all lots + fetch nearby
  loadAllLots()
  fetchNearbyLots(lat, lng)
}

function fallbackInit() {
  if (map) map.setView([DEFAULT_LAT, DEFAULT_LNG], 13)
  loadAllLots()
}

// ─── Load All Lots Markers ───
async function loadAllLots() {
  if (!map) return
  // Clear existing markers
  lotMarkers.forEach(m => map!.removeLayer(m))
  lotMarkers = []

  try {
    const res = await getAllLots()
    res.lots.forEach((lot: any) => {
      if (!lot.latitude || !lot.longitude) return

      const marker = L.marker([lot.latitude, lot.longitude], { icon: parkingIcon }).addTo(map!)

      const popupHtml = buildPopupHtml(lot)
      marker.bindPopup(popupHtml)

      // On marker click: draw route if user location known
      marker.on('click', () => {
        if (userLat.value !== null && userLng.value !== null) {
          drawRoute(lot.latitude, lot.longitude, lot.name || lot.parking_name)
        }
      })

      lotMarkers.push(marker)
    })
  } catch {
    error.value = 'Failed to load parking lots'
  }
}

function buildPopupHtml(lot: any) {
  const name = lot.name || lot.parking_name
  const escapedName = name.replace(/'/g, "\\'").replace(/"/g, '&quot;')
  const lotTypeHtml = lot.lot_type ? `<span style="background:#f3f4f6;border:1px solid #d1d5db;padding:1px 6px;font-size:10px;font-weight:700;text-transform:uppercase;color:#666;">${lot.lot_type.replace('_', ' ')}</span>` : ''
  const amenitiesHtml = lot.amenities ? `<div style="display:flex;gap:3px;flex-wrap:wrap;margin-bottom:6px;">${lot.amenities.split(',').map((a: string) => `<span style="background:#f9fafb;border:1px solid #e5e7eb;padding:1px 5px;font-size:9px;font-weight:600;color:#888;">${a.trim()}</span>`).join('')}</div>` : ''
  return `
    <div style="min-width:200px; font-family:'Poppins',sans-serif;">
      <h3 style="font-weight:700; font-size:14px; margin:0 0 4px;">${name}</h3>
      <p style="font-size:11px; color:#666; margin:0 0 6px;">${lot.address || ''}</p>
      <div style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:8px;">
        <span style="background:#000;color:#fff;padding:2px 8px;font-size:11px;font-weight:700;">₹${lot.price}/hr</span>
        <span style="background:${lot.free_spots > 0 ? '#16a34a' : '#dc2626'};color:#fff;padding:2px 8px;font-size:11px;font-weight:700;">${lot.free_spots} free</span>
        ${lot.distance_km !== undefined ? `<span style="background:#2563eb;color:#fff;padding:2px 8px;font-size:11px;font-weight:700;">${lot.distance_km} km</span>` : ''}
        ${lotTypeHtml}
      </div>
      ${amenitiesHtml}
      ${lot.free_spots > 0
        ? `<button onclick="window.__mapReserve(${lot.id},'${escapedName}',${lot.free_spots},${lot.price},'${(lot.address || '').replace(/'/g, "\\'")}')" style="width:100%;padding:8px;background:#000;color:#fff;border:none;font-weight:700;font-size:11px;text-transform:uppercase;letter-spacing:1px;cursor:pointer;">Reserve</button>`
        : `<p style="text-align:center;font-weight:700;color:#999;font-size:11px;text-transform:uppercase;">Full</p>`
      }
    </div>
  `
}

// ─── Nearby Lots ───
async function fetchNearbyLots(lat: number, lng: number) {
  nearbyLoading.value = true
  showNearbyPanel.value = true
  try {
    const res = await getNearbyLots(lat, lng, 5)
    nearbyLots.value = res.lots
  } catch {
    nearbyLots.value = []
  } finally {
    nearbyLoading.value = false
  }
}

function focusLot(lot: NearbyLot) {
  if (!map) return
  map.setView([lot.latitude, lot.longitude], 16)
  // Find the marker and open its popup
  const target = lotMarkers.find(m => {
    const ll = m.getLatLng()
    return Math.abs(ll.lat - lot.latitude) < 0.0001 && Math.abs(ll.lng - lot.longitude) < 0.0001
  })
  if (target) target.openPopup()
  // Draw route
  if (userLat.value !== null && userLng.value !== null) {
    drawRoute(lot.latitude, lot.longitude, lot.name)
  }
}

// ─── Route Drawing (OSRM via Leaflet Routing Machine) ───
async function loadRoutingEngine() {
  if (routingLoaded) return
  await import('leaflet-routing-machine/dist/leaflet-routing-machine.css')
  await import('leaflet-routing-machine')
  routingLoaded = true
}

async function drawRoute(destLat: number, destLng: number, destName: string) {
  if (!map || userLat.value === null || userLng.value === null) return

  // Remove existing route
  clearRoute()

  // Lazy-load routing engine on first use
  await loadRoutingEngine()

  routeTarget.value = destName
  showRouteInfo.value = true
  routeCalculating.value = true
  routeDistance.value = 'Calculating...'
  routeTime.value = ''

  routingControl = (L as any).Routing.control({
    waypoints: [
      L.latLng(userLat.value, userLng.value),
      L.latLng(destLat, destLng),
    ],
    router: (L as any).Routing.osrmv1({
      serviceUrl: 'https://router.project-osrm.org/route/v1',
      profile: 'driving',
    }),
    lineOptions: {
      styles: [{ color: '#000', weight: 5, opacity: 0.8 }],
      extendToWaypoints: true,
      missingRouteTolerance: 10,
    },
    addWaypoints: false,
    draggableWaypoints: false,
    fitSelectedRoutes: true,
    show: false,       // Hide the default itinerary panel
    createMarker: () => null,  // Don't add default markers (we have our own)
  }).addTo(map)

  routingControl.on('routesfound', (e: any) => {
    const route = e.routes[0]
    const distKm = (route.summary.totalDistance / 1000).toFixed(1)
    const timeMin = Math.round(route.summary.totalTime / 60)
    routeDistance.value = `${distKm} km`
    routeTime.value = timeMin < 60 ? `${timeMin} min` : `${Math.floor(timeMin / 60)}h ${timeMin % 60}m`
    routeCalculating.value = false
  })

  routingControl.on('routingerror', () => {
    routeDistance.value = 'Route unavailable'
    routeTime.value = ''
    routeCalculating.value = false
  })
}

function clearRoute() {
  if (routingControl && map) {
    map.removeControl(routingControl)
    routingControl = null
  }
  showRouteInfo.value = false
  routeTarget.value = null
}

// ─── Reserve ───
;(window as any).__mapReserve = (lotId: number, lotName: string, freeSpots: number, price: number, address: string) => {
  selectedLot.value = { id: lotId, name: lotName, free_spots: freeSpots, price, address }
  vehicleNumber.value = ''
  reserveError.value = ''
  showModal.value = true
}

async function handleReserve() {
  if (!selectedLot.value || !vehicleNumber.value.trim()) {
    reserveError.value = 'Vehicle number is required'
    return
  }
  reserveLoading.value = true
  reserveError.value = ''
  try {
    const res = await reserveSpot(selectedLot.value.id, vehicleNumber.value.trim())
    toast.success(res.message)
    router.push('/bookings')
  } catch (err: any) {
    reserveError.value = err.response?.data?.error || 'Failed to reserve spot'
  } finally {
    reserveLoading.value = false
  }
}

function goBack() {
  router.push('/book')
}

function relocate() {
  clearRoute()
  showNearbyPanel.value = false
  nearbyLots.value = []
  showLocationPrompt.value = true
}
</script>

<template>
  <div class="relative w-full h-screen overflow-hidden">
    <!-- Back + Relocate buttons -->
    <div class="absolute top-3 left-3 z-[1000] flex gap-1.5">
      <button @click="goBack" class="px-3 py-1.5 md:px-4 md:py-2 bg-black text-white font-bold text-[10px] md:text-xs uppercase tracking-wider shadow-lg hover:bg-gray-800 transition-colors">
        &larr; Back
      </button>
      <button v-if="userLat !== null" @click="relocate" class="px-3 py-1.5 md:px-4 md:py-2 bg-white text-black border-2 border-black font-bold text-[10px] md:text-xs uppercase tracking-wider shadow-lg hover:bg-gray-100 transition-colors">
        📍 Relocate
      </button>
    </div>

    <!-- Title overlay -->
    <div class="absolute top-3 left-1/2 -translate-x-1/2 z-[1000] bg-white/95 border-2 border-black px-3 py-1.5 md:px-5 md:py-2.5 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] text-center max-w-xs md:max-w-md w-[60%] md:w-[85%] pointer-events-none">
      <h2 class="text-xs md:text-base font-bold text-black uppercase tracking-tight">Find Nearest Parking</h2>
      <p class="text-[9px] md:text-[11px] text-gray-500 font-medium hidden sm:block">Set your location to see the 5 closest available lots</p>
    </div>

    <!-- Location Prompt Overlay -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div v-if="showLocationPrompt && !loading" class="absolute inset-0 z-[1500] flex items-center justify-center bg-black/50 px-4">
        <div class="bg-white border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] w-full max-w-sm p-6 md:p-8 text-center">
          <div class="w-12 h-12 md:w-16 md:h-16 bg-black text-white flex items-center justify-center mx-auto mb-3 md:mb-4 text-xl md:text-2xl">📍</div>
          <h3 class="text-lg md:text-xl font-bold text-black uppercase tracking-tight mb-2">Set Your Location</h3>
          <p class="text-xs md:text-sm text-gray-500 mb-5 md:mb-6">We need your location to find the nearest available parking lots.</p>
          <div class="space-y-3">
            <button
              @click="useGpsLocation"
              class="w-full py-3 md:py-3.5 bg-black text-white font-bold uppercase tracking-widest text-xs md:text-sm hover:bg-gray-800 transition-colors"
            >
              Use My GPS Location
            </button>
            <button
              @click="useManualPin"
              class="w-full py-3 md:py-3.5 bg-white text-black border-2 border-black font-bold uppercase tracking-widest text-xs md:text-sm hover:bg-gray-100 transition-colors"
            >
              Pin on Map Manually
            </button>
          </div>
          <button @click="showLocationPrompt = false; fallbackInit()" class="mt-3 md:mt-4 text-[10px] md:text-xs text-gray-400 hover:text-black font-medium">
            Skip — show all lots
          </button>
        </div>
      </div>
    </transition>

    <!-- Locating spinner -->
    <div v-if="locating && !showLocationPrompt" class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-[1200] bg-white border-2 border-black p-4 md:p-6 shadow-lg text-center">
      <div class="w-7 h-7 md:w-8 md:h-8 border-4 border-black border-t-transparent animate-spin mx-auto mb-2 md:mb-3"></div>
      <p class="font-bold text-xs md:text-sm text-black uppercase tracking-wider">Getting your location...</p>
    </div>

    <!-- Route Info Bar -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="translate-y-full opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="translate-y-full opacity-0"
    >
      <div v-if="showRouteInfo" class="absolute bottom-3 left-1/2 -translate-x-1/2 z-[1100] bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] px-3 py-2 md:px-5 md:py-3 flex items-center gap-3 md:gap-4 max-w-md w-[92%]">
        <div class="flex-1 min-w-0">
          <p class="text-[10px] md:text-xs text-gray-500 font-bold uppercase tracking-wider truncate">Route to {{ routeTarget }}</p>
          <div class="flex items-center gap-2 md:gap-3 mt-0.5 md:mt-1">
            <span class="text-base md:text-lg font-bold text-black">{{ routeDistance }}</span>
            <span v-if="routeTime" class="text-xs md:text-sm font-bold text-gray-600">~{{ routeTime }}</span>
          </div>
        </div>
        <button @click="clearRoute" class="px-2.5 py-1.5 md:px-3 md:py-2 bg-black text-white text-[10px] md:text-xs font-bold uppercase tracking-wider hover:bg-gray-800 transition-colors shrink-0">
          Clear
        </button>
      </div>
    </transition>

    <!-- Nearby Lots: Floating toggle button (shown when panel is collapsed) -->
    <button
      v-if="nearbyLots.length > 0 && (!showNearbyPanel || nearbyCollapsed)"
      @click="showNearbyPanel = true; nearbyCollapsed = false"
      class="absolute top-14 right-3 z-[1100] w-10 h-10 md:w-11 md:h-11 bg-black text-white flex items-center justify-center border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:bg-gray-800 transition-colors"
      title="Show nearby lots"
    >
      <span class="text-sm md:text-base font-bold">P</span>
      <span class="absolute -top-1.5 -left-1.5 w-5 h-5 bg-green-500 text-white text-[9px] font-bold rounded-full flex items-center justify-center">{{ nearbyLots.length }}</span>
    </button>

    <!-- Nearby Lots Panel -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="translate-y-full md:translate-y-0 md:translate-x-full"
      enter-to-class="translate-y-0 md:translate-x-0"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="translate-y-0 md:translate-x-0"
      leave-to-class="translate-y-full md:translate-y-0 md:translate-x-full"
    >
      <div
        v-if="showNearbyPanel && !nearbyCollapsed"
        class="absolute z-[1100] bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]
               bottom-0 left-0 right-0 max-h-[45vh] rounded-t-lg
               md:bottom-auto md:top-20 md:right-3 md:left-auto md:w-72 md:max-h-[calc(100vh-120px)] md:rounded-none
               overflow-y-auto"
      >
        <div class="bg-black text-white px-3 py-2.5 md:px-4 md:py-3 flex items-center justify-between sticky top-0 z-10">
          <h3 class="text-[10px] md:text-xs font-bold uppercase tracking-widest">Nearest Parking ({{ nearbyLots.length }})</h3>
          <button @click="nearbyCollapsed = true; showNearbyPanel = false" class="text-white/70 hover:text-white text-base md:text-lg leading-none">&times;</button>
        </div>

        <div v-if="nearbyLoading" class="p-4 md:p-6 text-center">
          <div class="w-5 h-5 md:w-6 md:h-6 border-3 border-black border-t-transparent animate-spin mx-auto"></div>
        </div>

        <div v-else-if="nearbyLots.length === 0" class="p-3 md:p-4 text-center text-xs md:text-sm text-gray-400 font-medium">
          No available parking lots found nearby.
        </div>

        <div v-else>
          <button
            v-for="(lot, idx) in nearbyLots"
            :key="lot.id"
            @click="focusLot(lot)"
            class="w-full text-left px-3 py-2.5 md:px-4 md:py-3 border-b border-gray-200 hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-start gap-2">
              <span class="w-5 h-5 md:w-6 md:h-6 bg-black text-white text-[10px] md:text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">{{ idx + 1 }}</span>
              <div class="min-w-0 flex-1">
                <p class="font-bold text-black text-xs md:text-sm truncate">{{ lot.name }}</p>
                <p class="text-[10px] md:text-[11px] text-gray-500 truncate">{{ lot.address }}</p>
                <div class="flex items-center gap-1.5 md:gap-2 mt-1 md:mt-1.5 flex-wrap">
                  <span class="text-[10px] md:text-[11px] font-bold text-blue-600 bg-blue-50 px-1 md:px-1.5 py-0.5">{{ lot.distance_km }} km</span>
                  <span class="text-[10px] md:text-[11px] font-bold text-green-700 bg-green-50 px-1 md:px-1.5 py-0.5">{{ lot.free_spots }} free</span>
                  <span class="text-[10px] md:text-[11px] font-bold text-gray-600">₹{{ lot.price }}/hr</span>
                </div>
              </div>
            </div>
          </button>
        </div>
      </div>
    </transition>

    <!-- Route Calculating Overlay -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="routeCalculating" class="absolute inset-0 z-[1500] flex items-center justify-center pointer-events-none">
        <div class="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] px-6 py-5 md:px-8 md:py-6 text-center pointer-events-auto">
          <div class="w-8 h-8 md:w-10 md:h-10 border-4 border-black border-t-transparent animate-spin mx-auto mb-3"></div>
          <p class="text-xs md:text-sm font-bold text-black uppercase tracking-wider">Calculating Route...</p>
          <p class="text-[10px] md:text-xs text-gray-400 mt-1">Finding the best path for you</p>
        </div>
      </div>
    </transition>

    <!-- Loading overlay -->
    <div v-if="loading" class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-[1000]">
      <div class="w-10 h-10 border-4 border-black border-t-transparent animate-spin"></div>
    </div>

    <!-- Map -->
    <div ref="mapContainer" class="w-full h-full"></div>

    <!-- Reserve Modal -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showModal" class="fixed inset-0 z-[2000] flex items-end md:items-center justify-center bg-black/60 px-0 md:px-4">
        <div class="bg-white border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] w-full max-w-md p-5 md:p-8 rounded-t-lg md:rounded-none">
          <h3 class="text-xl md:text-2xl font-bold text-black uppercase tracking-tighter mb-1 md:mb-2">Reserve Spot</h3>
          <p class="text-xs md:text-sm text-gray-500 mb-0.5 md:mb-1">{{ selectedLot?.name }}</p>
          <p v-if="selectedLot?.address" class="text-[10px] md:text-xs text-gray-400 mb-3 md:mb-4">{{ selectedLot.address }}</p>

          <div v-if="reserveError" class="mb-3 md:mb-4 p-2.5 md:p-3 bg-red-50 border-2 border-red-600 text-red-600 text-xs md:text-sm font-bold">{{ reserveError }}</div>

          <div class="flex gap-2 md:gap-3 mb-4 md:mb-5">
            <span v-if="selectedLot?.price" class="text-[10px] md:text-xs font-bold bg-black text-white px-2 py-1">₹{{ selectedLot.price }}/hr</span>
            <span v-if="selectedLot?.free_spots" class="text-[10px] md:text-xs font-bold bg-green-600 text-white px-2 py-1">{{ selectedLot.free_spots }} spots free</span>
          </div>

          <div class="space-y-3 md:space-y-4">
            <div>
              <label class="block text-xs md:text-sm font-bold text-black uppercase tracking-wider mb-1.5 md:mb-2">Vehicle Number</label>
              <input
                v-model="vehicleNumber"
                type="text"
                placeholder="MH12AB1234"
                class="w-full px-3 py-2.5 md:px-4 md:py-3 border-2 border-black focus:ring-0 focus:border-gray-600 outline-none text-xs md:text-sm font-medium uppercase"
              />
            </div>
          </div>

          <div class="flex gap-3 md:gap-4 mt-5 md:mt-8">
            <button
              @click="handleReserve"
              :disabled="reserveLoading"
              class="flex-1 py-2.5 md:py-3 bg-black text-white font-bold uppercase tracking-widest text-xs md:text-sm hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
            >
              {{ reserveLoading ? 'Reserving...' : 'Reserve Now' }}
            </button>
            <button
              @click="showModal = false"
              class="flex-1 py-2.5 md:py-3 bg-white text-black border-2 border-black font-bold uppercase tracking-widest text-xs md:text-sm hover:bg-gray-100 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>
