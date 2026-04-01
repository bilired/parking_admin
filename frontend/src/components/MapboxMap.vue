<template>
  <div ref="mapContainer" class="mapbox-container">
    <div v-if="!tokenLoaded" class="map-loading">
      <el-icon :size="32" class="spinning" color="#4f8ef7"><Loading /></el-icon>
      <p>地圖加載中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, nextTick, computed } from 'vue'
import mapboxgl from 'mapbox-gl'
import MapboxDirections from '@mapbox/mapbox-gl-directions/dist/mapbox-gl-directions'
import { ElMessage } from 'element-plus'
import { useCarparkStore } from '@/stores/carpark'
import type { CarparkInfo, VacancyMap } from '@/types'

const props = defineProps<{
  carparks: CarparkInfo[]
  selectedCarpark: CarparkInfo | null
  vacancyMap: VacancyMap
  favoriteIds?: string[]
  sidebarCollapsed?: boolean
  routeTarget?: CarparkInfo | null
  routeRequestId?: number
  streetViewTarget?: CarparkInfo | null
  streetViewRequestId?: number
}>()

const emit = defineEmits<{
  (e: 'select', carpark: CarparkInfo): void
}>()

const carparkStore = useCarparkStore()
const mapContainer = ref<HTMLDivElement | null>(null)
let map: mapboxgl.Map | null = null
const tokenLoaded = ref(false)
const SOURCE_ID = 'carparks-source'
const LAYER_ID = 'carparks-layer'
const FAVORITE_STAR_LAYER_ID = 'carparks-favorite-star-layer'
const HK_BBOX: [number, number, number, number] = [113.818, 22.153, 114.445, 22.561]
const MAP_STYLES = [
  { id: 'dark-v11', label: 'Dark', title: '深色底圖', swatch: 'dark' },
  { id: 'light-v11', label: 'Light', title: '淺色底圖', swatch: 'light' },
  { id: 'streets-v12', label: 'Street', title: '街道底圖', swatch: 'streets' },
  { id: 'outdoors-v12', label: 'Outdoor', title: '戶外底圖', swatch: 'outdoors' },
  { id: 'satellite-streets-v12', label: 'Sat', title: '衛星底圖', swatch: 'satellite' },
] as const
const currentStyleId = ref<(typeof MAP_STYLES)[number]['id']>('streets-v12')
const favoriteIdSet = computed(() => new Set(props.favoriteIds ?? []))

class DirectionsToggleControl implements mapboxgl.IControl {
  private container?: HTMLDivElement
  private button?: HTMLButtonElement

  constructor(
    private readonly isExpanded: () => boolean,
    private readonly onToggle: () => void,
  ) {}

  onAdd(): HTMLElement {
    const container = document.createElement('div')
    container.className = 'mapboxgl-ctrl mapboxgl-ctrl-group'

    const button = document.createElement('button')
    button.type = 'button'
    button.className = 'mapboxgl-ctrl-icon directions-toggle-btn'
    button.title = '導航面板'
    button.setAttribute('aria-label', '導航面板')
    button.addEventListener('click', () => {
      this.onToggle()
      this.updateState()
    })

    container.appendChild(button)
    this.container = container
    this.button = button
    this.updateState()
    return container
  }

  onRemove(): void {
    this.container?.remove()
    this.container = undefined
    this.button = undefined
  }

  updateState(): void {
    if (!this.button) return
    const expanded = this.isExpanded()
    this.button.innerHTML = '<span class="map-control-logo map-control-logo--directions" aria-hidden="true"></span>'
    this.button.classList.toggle('is-active', expanded)
    this.button.setAttribute('aria-pressed', String(expanded))
  }
}


class StyleSwitcherControl implements mapboxgl.IControl {
  private container?: HTMLDivElement
  private map?: mapboxgl.Map
  private list?: HTMLDivElement
  private triggerButton?: HTMLButtonElement
  private expanded = false
  private readonly handleDocumentClick = (event: MouseEvent) => {
    if (!this.container) return
    if (event.target instanceof Node && this.container.contains(event.target)) return
    this.setExpanded(false)
  }

  constructor(
    private readonly styles: readonly { id: string; label: string; title: string; swatch: string }[],
    private readonly getActiveStyleId: () => string,
    private readonly onStyleChange: (styleId: string) => void,
  ) {}

  onAdd(mapInstance: mapboxgl.Map): HTMLElement {
    this.map = mapInstance
    const container = document.createElement('div')
    container.className = 'mapboxgl-ctrl mapboxgl-ctrl-group map-style-switcher'

    const triggerButton = document.createElement('button')
    triggerButton.type = 'button'
    triggerButton.className = 'mapboxgl-ctrl-icon map-style-switcher__trigger'
    triggerButton.setAttribute('aria-label', '切換地圖底圖')
    triggerButton.setAttribute('aria-expanded', 'false')
    triggerButton.addEventListener('click', () => {
      this.setExpanded(!this.expanded)
    })

    const list = document.createElement('div')
    list.className = 'map-style-switcher__list'

    this.styles.forEach((styleItem) => {
      const button = document.createElement('button')
      button.type = 'button'
      button.className = 'mapboxgl-ctrl-icon map-style-switcher__btn'
      button.dataset.styleId = styleItem.id
      button.dataset.swatch = styleItem.swatch
      button.title = styleItem.title
      button.setAttribute('aria-label', styleItem.title)

      const swatch = document.createElement('span')
      swatch.className = 'map-style-switcher__swatch'
      swatch.setAttribute('aria-hidden', 'true')

      const text = document.createElement('span')
      text.className = 'map-style-switcher__text'
      text.textContent = styleItem.label

      button.appendChild(swatch)
      button.appendChild(text)
      button.addEventListener('click', () => {
        if (this.getActiveStyleId() === styleItem.id) return
        this.onStyleChange(styleItem.id)
        this.setExpanded(false)
        this.updateActiveState()
      })
      list.appendChild(button)
    })

    container.appendChild(triggerButton)
    container.appendChild(list)
    this.container = container
    this.list = list
    this.triggerButton = triggerButton
    this.updateActiveState()
    document.addEventListener('click', this.handleDocumentClick)
    return container
  }

  onRemove(): void {
    document.removeEventListener('click', this.handleDocumentClick)
    this.container?.remove()
    this.container = undefined
    this.list = undefined
    this.triggerButton = undefined
    this.map = undefined
  }

  setExpanded(expanded: boolean): void {
    this.expanded = expanded
    this.container?.classList.toggle('is-expanded', expanded)
    this.triggerButton?.setAttribute('aria-expanded', String(expanded))
  }

  updateActiveState(): void {
    if (!this.container) return
    const activeStyleId = this.getActiveStyleId()
    const activeStyle = this.styles.find((style) => style.id === activeStyleId)

    this.container.querySelectorAll<HTMLButtonElement>('.map-style-switcher__btn').forEach((button) => {
      const isActive = button.dataset.styleId === activeStyleId
      button.classList.toggle('is-active', isActive)
      button.setAttribute('aria-pressed', String(isActive))
    })

    if (this.triggerButton && activeStyle) {
      this.triggerButton.dataset.swatch = activeStyle.swatch
      this.triggerButton.innerHTML = '<span class="map-control-logo map-control-logo--style" aria-hidden="true"></span>'
      this.triggerButton.classList.toggle('is-active', this.expanded)
    }
  }
}

let styleSwitcherControl: StyleSwitcherControl | null = null
let directionsControl: MapboxDirections | null = null
let directionsToggleControl: DirectionsToggleControl | null = null
let geolocateControl: mapboxgl.GeolocateControl | null = null
let syncTimer: number | null = null
let currentUserLocation: [number, number] | null = null
const directionsExpanded = ref(false)
const activeDirectionsField = ref<'origin' | 'destination' | null>(null)
let directionsInputArmingCleanup: (() => void) | null = null

function getDirectionsControlElement(): HTMLElement | null {
  if (!map) return null
  return map.getContainer().querySelector('.mapboxgl-ctrl-directions') as HTMLElement | null
}

function setDirectionsExpanded(expanded: boolean) {
  directionsExpanded.value = expanded
  if (!expanded) activeDirectionsField.value = null
  const el = getDirectionsControlElement()
  if (el) {
    el.classList.toggle('map-directions-collapsed', !expanded)
  }
  directionsToggleControl?.updateState()
}

function toggleDirectionsPanel() {
  setDirectionsExpanded(!directionsExpanded.value)
}

function bindDirectionsInputArming() {
  directionsInputArmingCleanup?.()
  directionsInputArmingCleanup = null

  const directionsEl = getDirectionsControlElement()
  if (!directionsEl) return

  const armFromEventTarget = (target: EventTarget | null) => {
    if (!(target instanceof HTMLElement)) return
    const originHost = target.closest('.mapbox-directions-origin')
    const destinationHost = target.closest('.mapbox-directions-destination')

    if (originHost) {
      activeDirectionsField.value = 'origin'
      return
    }
    if (destinationHost) {
      activeDirectionsField.value = 'destination'
    }
  }

  const onFocusIn = (event: FocusEvent) => {
    if (!directionsExpanded.value) return
    armFromEventTarget(event.target)
  }

  const onMouseDown = (event: MouseEvent) => {
    if (!directionsExpanded.value) return
    armFromEventTarget(event.target)
  }

  directionsEl.addEventListener('focusin', onFocusIn)
  directionsEl.addEventListener('mousedown', onMouseDown)

  directionsInputArmingCleanup = () => {
    directionsEl.removeEventListener('focusin', onFocusIn)
    directionsEl.removeEventListener('mousedown', onMouseDown)
  }
}

function handleMapClickForDirections(event: mapboxgl.MapMouseEvent) {
  if (!directionsControl || !directionsExpanded.value || !activeDirectionsField.value) return

  const coords: [number, number] = [event.lngLat.lng, event.lngLat.lat]
  if (activeDirectionsField.value === 'origin') {
    directionsControl.setOrigin(coords)
  } else {
    directionsControl.setDestination(coords)
  }

  activeDirectionsField.value = null
}

function handleLayerClick(event: mapboxgl.MapLayerMouseEvent) {
  const feature = event.features?.[0]
  const carparkNo = feature?.properties?.carparkNo
  if (!carparkNo) return

  const carpark = props.carparks.find((item) => item.carparkNo === carparkNo)
  if (carpark) emit('select', carpark)
}

function handleLayerMouseEnter() {
  if (map) map.getCanvas().style.cursor = 'pointer'
}

function handleLayerMouseLeave() {
  if (map) map.getCanvas().style.cursor = ''
}

function rememberUserLocation(coords: GeolocationCoordinates | { longitude: number; latitude: number }) {
  currentUserLocation = [coords.longitude, coords.latitude]
}

function requestCurrentLocation(): Promise<[number, number] | null> {
  if (currentUserLocation) return Promise.resolve(currentUserLocation)
  if (!navigator.geolocation) return Promise.resolve(null)

  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        rememberUserLocation(position.coords)
        resolve(currentUserLocation)
      },
      () => resolve(null),
      { enableHighAccuracy: true, timeout: 8000 }
    )
  })
}

function getVacancyColor(carparkNo: string): string {
  const total = carparkStore.getVacancySummary(carparkNo)
  if (total === null) return '#4f8ef7'
  if (total === 0) return '#e74c3c'
  if (total < 10) return '#f5a623'
  return '#26c281'
}

function buildGeoJson(carparks: CarparkInfo[]) {
  const favorites = favoriteIdSet.value
  return {
    type: 'FeatureCollection' as const,
    features: carparks
      .filter((cp) => cp.latitude != null && cp.longitude != null)
      .map((cp) => ({
        type: 'Feature' as const,
        geometry: {
          type: 'Point' as const,
          coordinates: [cp.longitude as number, cp.latitude as number],
        },
        properties: {
          carparkNo: cp.carparkNo,
          color: getVacancyColor(cp.carparkNo),
          isSelected: props.selectedCarpark?.carparkNo === cp.carparkNo,
          isFavorite: favorites.has(cp.carparkNo),
        },
      })),
  }
}

function bindLayerEvents() {
  if (!map) return

  const bindForLayer = (layerId: string) => {
    if (!map?.getLayer(layerId)) return
    map.off('click', layerId, handleLayerClick)
    map.off('mouseenter', layerId, handleLayerMouseEnter)
    map.off('mouseleave', layerId, handleLayerMouseLeave)

    map.on('click', layerId, handleLayerClick)
    map.on('mouseenter', layerId, handleLayerMouseEnter)
    map.on('mouseleave', layerId, handleLayerMouseLeave)
  }

  bindForLayer(LAYER_ID)
  bindForLayer(FAVORITE_STAR_LAYER_ID)
}

function updateMapSource(retryCount = 8) {
  if (!map) return

  if (!map.isStyleLoaded()) {
    if (retryCount > 0) {
      if (syncTimer !== null) window.clearTimeout(syncTimer)
      syncTimer = window.setTimeout(() => updateMapSource(retryCount - 1), 120)
    }
    return
  }

  const data = buildGeoJson(props.carparks)
  const source = map.getSource(SOURCE_ID) as mapboxgl.GeoJSONSource | undefined

  if (source) {
    source.setData(data)
  } else {
    map.addSource(SOURCE_ID, {
      type: 'geojson',
      data,
    })
  }

  if (!map.getLayer(LAYER_ID)) {
    map.addLayer({
      id: LAYER_ID,
      type: 'circle',
      source: SOURCE_ID,
      paint: {
        'circle-color': ['get', 'color'],
        'circle-radius': ['case', ['get', 'isSelected'], 10, 7],
        'circle-stroke-color': '#ffffff',
        'circle-stroke-width': ['case', ['get', 'isSelected'], 3, 2],
        'circle-opacity': 1,
        'circle-pitch-alignment': 'map',
        'circle-stroke-opacity': 1,
      },
    })
  }

  if (!map.getLayer(FAVORITE_STAR_LAYER_ID)) {
    map.addLayer({
      id: FAVORITE_STAR_LAYER_ID,
      type: 'symbol',
      source: SOURCE_ID,
      filter: ['==', ['get', 'isFavorite'], true],
      layout: {
        'text-field': '★',
        'text-size': 12,
        'text-font': ['Open Sans Bold', 'Arial Unicode MS Bold'],
        'text-anchor': 'center',
        'text-offset': [0, -1.1],
        'text-allow-overlap': true,
        'text-ignore-placement': true,
      },
      paint: {
        'text-color': '#ffffff',
        'text-halo-color': '#d89b34',
        'text-halo-width': 2.2,
        'text-halo-blur': 0.5,
      },
    })
  }

  bindLayerEvents()
}

function changeMapStyle(styleId: (typeof MAP_STYLES)[number]['id']) {
  if (!map) return
  currentStyleId.value = styleId
  map.setStyle(`mapbox://styles/mapbox/${styleId}`)
  map.once('style.load', () => {
    updateMapSource()
    styleSwitcherControl?.updateActiveState()
  })
}

function getStreetViewTargetCoords(): [number, number] | null {
  if (props.selectedCarpark?.longitude != null && props.selectedCarpark.latitude != null) {
    return [props.selectedCarpark.longitude, props.selectedCarpark.latitude]
  }

  if (currentUserLocation) {
    return currentUserLocation
  }

  if (!map) return null
  const center = map.getCenter()
  return [center.lng, center.lat]
}

function openStreetViewAt(coords: [number, number] | null) {
  if (!coords) {
    ElMessage.warning('目前沒有可用位置，請先選擇停車場或移動地圖')
    return
  }

  const [lng, lat] = coords
  const url = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lng}`
  const newWindow = window.open(url, '_blank', 'noopener,noreferrer')
  if (!newWindow) {
    ElMessage.warning('無法開啟街景視窗，請檢查瀏覽器彈出視窗設定')
  }
}


async function startNavigationTo(target: CarparkInfo | null) {
  if (!target || !directionsControl || target.longitude == null || target.latitude == null) {
    return
  }

  setDirectionsExpanded(true)

  directionsControl.setDestination([target.longitude, target.latitude])
  const origin = await requestCurrentLocation()

  if (origin) {
    directionsControl.setOrigin(origin)
  } else {
    ElMessage.info('無法取得目前位置，請在路線面板中手動輸入起點')
  }

  if (map) {
    map.flyTo({
      center: [target.longitude, target.latitude],
      zoom: 14,
      duration: 600,
    })
  }
}

function flyToCarpark(cp: CarparkInfo) {
  if (!map || cp.latitude == null || cp.longitude == null) return
  map.flyTo({
    center: [cp.longitude, cp.latitude],
    zoom: 16,
    duration: 800,
  })
}

async function initMap() {
  const token = await carparkStore.fetchMapboxToken()
  if (!token || !mapContainer.value) return

  mapboxgl.accessToken = token
  tokenLoaded.value = true

  await nextTick()

  map = new mapboxgl.Map({
    container: mapContainer.value,
    style: `mapbox://styles/mapbox/${currentStyleId.value}`,
    center: [114.1694, 22.3193], // Hong Kong center
    zoom: 12,
    attributionControl: false,
  })

  directionsControl = new MapboxDirections({
    accessToken: token,
    interactive: false,
    language: 'zh-tw',
    unit: 'metric',
    profile: 'mapbox/driving',
    geocoder: {
      countries: 'hk',
      bbox: HK_BBOX,
      language: 'zh-Hant',
    },
    controls: {
      inputs: true,
      instructions: true,
      profileSwitcher: true,
    },
    flyTo: false,
  })
  map.addControl(directionsControl, 'top-left')
  bindDirectionsInputArming()
  map.on('click', handleMapClickForDirections)

  geolocateControl = new mapboxgl.GeolocateControl({
    positionOptions: { enableHighAccuracy: true },
    trackUserLocation: true,
    showUserHeading: true,
  })
  geolocateControl.on('geolocate', (event) => {
    rememberUserLocation(event.coords)
  })
  map.addControl(geolocateControl, 'top-right')

  map.addControl(new mapboxgl.NavigationControl(), 'top-right')
  directionsToggleControl = new DirectionsToggleControl(
    () => directionsExpanded.value,
    () => toggleDirectionsPanel(),
  )
  map.addControl(directionsToggleControl, 'top-right')
  styleSwitcherControl = new StyleSwitcherControl(
    MAP_STYLES,
    () => currentStyleId.value,
    (styleId) => changeMapStyle(styleId as (typeof MAP_STYLES)[number]['id'])
  )
  map.addControl(styleSwitcherControl, 'top-right')
  map.addControl(new mapboxgl.AttributionControl({ compact: true }), 'bottom-right')

  map.on('load', () => {
    updateMapSource()
    setDirectionsExpanded(false)
  })

  map.on('style.load', () => {
    updateMapSource()
    styleSwitcherControl?.updateActiveState()
  })

  map.on('idle', () => {
    if (!map?.getLayer(LAYER_ID) || !map?.getSource(SOURCE_ID)) {
      updateMapSource()
    }
  })
}

watch(
  () => [props.carparks, props.vacancyMap, props.selectedCarpark?.carparkNo, props.favoriteIds],
  () => {
    updateMapSource()
  },
  { deep: true }
)

watch(
  () => props.selectedCarpark,
  (cp) => {
    if (cp) flyToCarpark(cp)
    updateMapSource()
  }
)

watch(
  () => props.sidebarCollapsed,
  () => {
    window.setTimeout(() => {
      map?.resize()
    }, 320)
  }
)

watch(
  () => props.routeRequestId,
  () => {
    startNavigationTo(props.routeTarget ?? null)
  }
)



onMounted(async () => {
  await initMap()
})

onBeforeUnmount(() => {
  if (syncTimer !== null) window.clearTimeout(syncTimer)
  directionsInputArmingCleanup?.()
  directionsInputArmingCleanup = null
  if (map) {
    map.off('click', handleMapClickForDirections)
  }
  map?.remove()
  map = null
  styleSwitcherControl = null
  directionsControl = null
  directionsToggleControl = null
  geolocateControl = null
  currentUserLocation = null
  directionsExpanded.value = false
})
</script>

<style scoped>
.mapbox-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.map-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  gap: 12px;
  color: var(--text-secondary);
  font-size: 14px;
  z-index: 5;
}

.spinning {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>

<style>
/* Global mapbox overrides */
.mapboxgl-canvas {
  outline: none;
}
.mapboxgl-ctrl-group {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
}
.mapboxgl-ctrl-top-left {
  top: 16px;
  left: 16px;
}
.mapboxgl-ctrl-top-right {
  top: 16px;
  right: 16px;
}
.mapboxgl-ctrl-group button {
  background-color: var(--bg-card) !important;
}
.mapboxgl-ctrl-group button .mapboxgl-ctrl-icon {
  filter: none;
}
.mapbox-directions-component,
.directions-control,
.mapboxgl-ctrl-directions {
  background: rgba(255, 255, 255, 0.98) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  color: #1f3552 !important;
  box-shadow: 0 18px 40px rgba(47, 126, 247, 0.12) !important;
}
.mapboxgl-ctrl-directions {
  min-width: 320px;
}
.mapboxgl-ctrl-top-left .mapboxgl-ctrl-directions {
  margin-left: 4px !important;
}
.mapboxgl-ctrl-directions.map-directions-collapsed {
  display: none !important;
}
.directions-toggle-btn {
  width: 30px !important;
  min-width: 30px;
  padding: 0;
  color: var(--text-primary) !important;
  background-image: none !important;
  filter: none !important;
}
.directions-toggle-btn:hover {
  color: var(--accent) !important;
}
.directions-toggle-btn.is-active,
.map-style-switcher__trigger.is-active {
  box-shadow: inset 0 0 0 1px rgba(79, 142, 247, 0.45);
}
.map-style-switcher .map-style-switcher__trigger {
  width: 30px;
  min-width: 30px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.map-control-logo {
  width: 14px;
  height: 14px;
  display: inline-block;
  position: relative;
}
.map-control-logo--style::before,
.map-control-logo--style::after {
  content: '';
  position: absolute;
  border: 1.6px solid currentColor;
  border-radius: 2px;
  transform: rotate(-8deg);
}
.map-control-logo--style::before {
  width: 10px;
  height: 8px;
  left: 2px;
  top: 2px;
  opacity: 0.95;
}
.map-control-logo--style::after {
  width: 10px;
  height: 8px;
  left: 0;
  top: 4px;
  opacity: 0.7;
}
.map-control-logo--directions::before {
  content: '';
  position: absolute;
  left: 2px;
  top: 6px;
  width: 9px;
  height: 0;
  border-top: 1.8px solid currentColor;
}
.map-control-logo--directions::after {
  content: '';
  position: absolute;
  right: 1px;
  top: 3px;
  width: 0;
  height: 0;
  border-left: 5px solid currentColor;
  border-top: 4px solid transparent;
  border-bottom: 4px solid transparent;
}
.mapbox-directions-origin input,
.mapbox-directions-destination input,
.directions-icon-depart,
.directions-icon-arrive {
  color: var(--text-primary) !important;
}
.mapboxgl-ctrl-directions input {
  background: transparent !important;
  color: #111111 !important;
  caret-color: #111111 !important;
}
.mapboxgl-ctrl-directions input::placeholder {
  color: #666666 !important;
}
.mapboxgl-ctrl-directions .suggestions,
.mapboxgl-ctrl-directions .suggestions > li,
.mapboxgl-ctrl-directions .suggestions a,
.mapboxgl-ctrl-directions .suggestions .mapboxgl-ctrl-geocoder--suggestion,
.mapboxgl-ctrl-directions .suggestions .mapboxgl-ctrl-geocoder--suggestion-title,
.mapboxgl-ctrl-directions .suggestions .mapboxgl-ctrl-geocoder--suggestion-address,
.mapboxgl-ctrl-directions .suggestions .name,
.mapboxgl-ctrl-directions .suggestions .type {
  color: #111111 !important;
}
.mapboxgl-ctrl-directions .suggestions > li.active a,
.mapboxgl-ctrl-directions .suggestions > li a:hover,
.mapboxgl-ctrl-directions .suggestions .mapboxgl-ctrl-geocoder--suggestion:hover {
  color: #111111 !important;
}
.mapboxgl-ctrl-directions,
.mapboxgl-ctrl-directions *,
.directions-control,
.directions-control *,
.directions-control-directions,
.directions-control-directions *,
.directions-control-instructions,
.directions-control-instructions * {
  color: #111111 !important;
}
.mapboxgl-ctrl-directions button,
.mapboxgl-ctrl-directions button span,
.directions-icon,
.directions-icon-reverse,
.directions-icon-route,
.directions-icon-depart,
.directions-icon-arrive {
  color: #111111 !important;
  fill: #111111 !important;
}
.directions-control-instructions .mapbox-directions-instructions .directions-icon,
.directions-control-instructions .mapbox-directions-step .directions-icon,
.directions-control-instructions .mapbox-directions-step [class*='directions-icon-'] {
  filter: brightness(0) saturate(100%) !important;
}
.mapboxgl-ctrl-directions .directions-reverse,
.mapboxgl-ctrl-directions .directions-icon-reverse,
.mapboxgl-ctrl-directions .mapbox-directions-inputs .directions-icon-reverse,
.mapboxgl-ctrl-directions .mapbox-directions-inputs button [class*='directions-icon-'] {
  filter: none !important;
}
.directions-control-instructions,
.directions-control-directions {
  background: rgba(255, 255, 255, 0.98) !important;
  color: #111111 !important;
}
.directions-route-summary,
.directions-step,
.directions-icon {
  color: #111111 !important;
}
.map-style-switcher {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 30px;
  width: 30px;
  transition: width 0.2s ease;
}
.map-style-switcher .map-style-switcher__list {
  display: none;
  flex-direction: column;
  border-top: 1px solid var(--border);
}
.map-style-switcher.is-expanded .map-style-switcher__list {
  display: flex;
}
.map-style-switcher.is-expanded {
  min-width: 112px;
  width: 112px;
}
.map-style-switcher .map-style-switcher__trigger {
  width: 30px;
  min-width: 30px;
  height: 30px;
  padding: 0;
  color: var(--text-primary);
  font-size: 11px;
  font-weight: 600;
  line-height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  text-align: center;
  background-image: none !important;
  filter: none !important;
}
.map-style-switcher.is-expanded .map-style-switcher__trigger {
  width: 112px;
  min-width: 112px;
  padding: 0 8px;
}
.map-style-switcher .map-style-switcher__btn {
  width: auto;
  min-width: 112px;
  height: 30px;
  padding: 0 8px;
  color: var(--text-primary);
  font-size: 11px;
  font-weight: 600;
  line-height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  text-align: center;
  background-image: none !important;
  filter: none !important;
}
.map-style-switcher .map-style-switcher__text {
  display: inline-block;
}
.map-style-switcher .map-style-switcher__caret {
  margin-left: auto;
  font-size: 10px;
  opacity: 0.8;
}
.map-style-switcher .map-style-switcher__swatch {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  border: 1px solid rgba(255, 255, 255, 0.35);
  flex-shrink: 0;
}
.map-style-switcher .map-style-switcher__trigger[data-swatch='dark'] .map-style-switcher__swatch,
.map-style-switcher .map-style-switcher__btn[data-swatch='dark'] .map-style-switcher__swatch {
  background: linear-gradient(135deg, #173257 0%, #3f6ea6 100%);
}
.map-style-switcher .map-style-switcher__trigger[data-swatch='light'] .map-style-switcher__swatch,
.map-style-switcher .map-style-switcher__btn[data-swatch='light'] .map-style-switcher__swatch {
  background: linear-gradient(135deg, #f3f5f7 0%, #cfd6df 100%);
}
.map-style-switcher .map-style-switcher__trigger[data-swatch='streets'] .map-style-switcher__swatch,
.map-style-switcher .map-style-switcher__btn[data-swatch='streets'] .map-style-switcher__swatch {
  background: linear-gradient(135deg, #f6edd6 0%, #c5d8c3 100%);
}
.map-style-switcher .map-style-switcher__trigger[data-swatch='outdoors'] .map-style-switcher__swatch,
.map-style-switcher .map-style-switcher__btn[data-swatch='outdoors'] .map-style-switcher__swatch {
  background: linear-gradient(135deg, #7fb069 0%, #d4a373 100%);
}
.map-style-switcher .map-style-switcher__trigger[data-swatch='satellite'] .map-style-switcher__swatch,
.map-style-switcher .map-style-switcher__btn[data-swatch='satellite'] .map-style-switcher__swatch {
  background: linear-gradient(135deg, #345c3f 0%, #7ea16b 50%, #4a4f57 100%);
}
.map-style-switcher .map-style-switcher__trigger:hover,
.map-style-switcher .map-style-switcher__btn:hover {
  background-color: var(--bg-secondary) !important;
}
.map-style-switcher .map-style-switcher__btn.is-active {
  color: #ffffff;
  background-color: var(--accent) !important;
}
</style>
