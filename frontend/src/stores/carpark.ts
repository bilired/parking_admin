import { defineStore } from 'pinia'
import { ref } from 'vue'
import { carparkApi, favoriteApi } from '@/api/carparks'
import type { CarparkInfo, Favorite, FavoritePayload, VacancyMap } from '@/types'

export const useCarparkStore = defineStore('carpark', () => {
  const carparks = ref<CarparkInfo[]>([])
  const favorites = ref<Favorite[]>([])
  const vacancyMap = ref<VacancyMap>({})
  const districts = ref<string[]>([])
  const mapboxToken = ref<string>('')
  const total = ref(0)
  const loading = ref(false)
  const selectedCarpark = ref<CarparkInfo | null>(null)

  async function fetchCarparks(params?: { search?: string; district?: string }) {
    loading.value = true
    try {
      const { data } = await carparkApi.list(params)
      carparks.value = data.carparks
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  async function fetchVacancy(ids?: string[]) {
    const { data } = await carparkApi.vacancy(ids)
    vacancyMap.value = { ...vacancyMap.value, ...data.vacancies }
  }

  async function fetchDistricts() {
    const { data } = await carparkApi.districts()
    districts.value = data.districts
  }

  async function fetchMapboxToken() {
    if (mapboxToken.value) return mapboxToken.value
    const { data } = await carparkApi.mapboxToken()
    mapboxToken.value = data.token
    return data.token
  }

  async function fetchFavorites() {
    const { data } = await favoriteApi.list()
    favorites.value = data
  }

  async function addFavorite(payload: FavoritePayload) {
    const { data } = await favoriteApi.add(payload)
    favorites.value.unshift(data)
    // Mark in carparks list
    const cp = carparks.value.find((c) => c.carparkNo === payload.carpark_id)
    if (cp) cp.isFavorite = true
    return data
  }

  async function removeFavorite(carparkId: string) {
    await favoriteApi.remove(carparkId)
    favorites.value = favorites.value.filter((f) => f.carpark_id !== carparkId)
    const cp = carparks.value.find((c) => c.carparkNo === carparkId)
    if (cp) cp.isFavorite = false
  }

  function isFavorite(carparkId: string) {
    return favorites.value.some((f) => f.carpark_id === carparkId)
  }

  function selectCarpark(carpark: CarparkInfo | null) {
    selectedCarpark.value = carpark
  }

  function getVacancySummary(carparkNo: string): number | null {
    const entries = vacancyMap.value[carparkNo]
    if (!entries || entries.length === 0) return null

    const validEntries = entries.filter((entry) => typeof entry.vacancy === 'number' && entry.vacancy >= 0)
    if (validEntries.length === 0) return null

    return validEntries.reduce((sum, entry) => sum + entry.vacancy, 0)
  }

  return {
    carparks,
    favorites,
    vacancyMap,
    districts,
    mapboxToken,
    total,
    loading,
    selectedCarpark,
    fetchCarparks,
    fetchVacancy,
    fetchDistricts,
    fetchMapboxToken,
    fetchFavorites,
    addFavorite,
    removeFavorite,
    isFavorite,
    selectCarpark,
    getVacancySummary,
  }
})
