<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps<{
  latitude?: number | null
  longitude?: number | null
}>()

const emit = defineEmits<{
  (e: 'update:latitude', val: number): void
  (e: 'update:longitude', val: number): void
}>()

const mapContainer = ref<HTMLDivElement | null>(null)
let map: L.Map | null = null
let marker: L.Marker | null = null

const DEFAULT_LAT = 23.2599
const DEFAULT_LNG = 77.4126

onMounted(() => {
  if (!mapContainer.value) return

  const lat = props.latitude ?? DEFAULT_LAT
  const lng = props.longitude ?? DEFAULT_LNG

  map = L.map(mapContainer.value).setView([lat, lng], 13)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map)

  // Place initial marker if coords provided
  if (props.latitude && props.longitude) {
    marker = L.marker([props.latitude, props.longitude]).addTo(map)
  }

  map.on('click', (e: L.LeafletMouseEvent) => {
    const { lat, lng } = e.latlng
    const newLat = parseFloat(lat.toFixed(6))
    const newLng = parseFloat(lng.toFixed(6))

    if (marker && map) {
      map.removeLayer(marker)
    }
    if (map) {
      marker = L.marker([newLat, newLng]).addTo(map)
    }

    emit('update:latitude', newLat)
    emit('update:longitude', newLng)
  })

  // Fix Leaflet icon paths (common Webpack/Vite issue)
  delete (L.Icon.Default.prototype as any)._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  })
})

watch(() => [props.latitude, props.longitude], ([lat, lng]) => {
  if (map && lat && lng) {
    map.setView([lat, lng], 13)
    if (marker) map.removeLayer(marker)
    marker = L.marker([lat, lng]).addTo(map)
  }
})
</script>

<template>
  <div>
    <label class="block text-sm font-bold text-black uppercase tracking-wider mb-2">Select Location on Map</label>
    <div ref="mapContainer" class="w-full h-[400px] border-2 border-black"></div>
    <p class="text-xs text-gray-400 mt-1">Click on the map to set the parking lot location.</p>
  </div>
</template>
