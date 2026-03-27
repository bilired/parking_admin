import request from './request'
import type {
  CarparkListResponse,
  VacancyResponse,
  Favorite,
  FavoritePayload,
} from '@/types'

export const carparkApi = {
  list(params?: { search?: string; district?: string }) {
    return request.get<CarparkListResponse>('/carparks/', { params })
  },
  vacancy(ids?: string[]) {
    const params = ids && ids.length > 0 ? { ids: ids.join(',') } : undefined
    return request.get<VacancyResponse>('/carparks/vacancy/', { params })
  },
  districts() {
    return request.get<{ districts: string[] }>('/carparks/districts/')
  },
  mapboxToken() {
    return request.get<{ token: string }>('/config/mapbox-token/')
  },
}

export const favoriteApi = {
  list() {
    return request.get<Favorite[]>('/favorites/')
  },
  add(data: FavoritePayload) {
    return request.post<Favorite>('/favorites/add/', data)
  },
  remove(carparkId: string) {
    return request.delete(`/favorites/${carparkId}/`)
  },
  check(carparkId: string) {
    return request.get<{ isFavorite: boolean }>(`/favorites/check/${carparkId}/`)
  },
}
