declare module '@mapbox/mapbox-gl-directions/dist/mapbox-gl-directions' {
  import type mapboxgl from 'mapbox-gl'

  interface DirectionsOptions {
    accessToken: string
    interactive?: boolean
    unit?: 'imperial' | 'metric'
    profile?: string
    flyTo?: boolean
    geocoder?: {
      countries?: string
      bbox?: [number, number, number, number]
      language?: string
    }
    controls?: {
      inputs?: boolean
      instructions?: boolean
      profileSwitcher?: boolean
    }
  }

  export default class MapboxDirections implements mapboxgl.IControl {
    constructor(options: DirectionsOptions)
    onAdd(map: mapboxgl.Map): HTMLElement
    onRemove(map: mapboxgl.Map): void
    setOrigin(origin: string | [number, number]): void
    setDestination(destination: string | [number, number]): void
    interactive(state: boolean): MapboxDirections
    removeRoutes(): void
  }
}