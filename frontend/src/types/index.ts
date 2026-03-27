// ======== Auth Types ========
export interface User {
  id: number
  username: string
  email: string
  phone: string
  created_at: string
}

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  username: string
  email: string
  phone?: string
  password: string
  password2: string
}

export interface AuthResponse {
  message: string
  user: User
  access: string
  refresh: string
}

// ======== Carpark Types ========
export interface VehicleTypeService {
  serviceCategory: string
  height?: number
  remark?: string
}

export interface VehicleType {
  vehicleType: string
  service?: VehicleTypeService[]
}

export interface CarparkInfo {
  carparkNo: string
  name: string
  nameEn?: string
  districtTc?: string
  districtEn?: string
  addressTc?: string
  addressEn?: string
  latitude?: number
  longitude?: number
  contactNo?: string
  website?: string
  openingHours?: string
  vehicleTypes?: VehicleType[]
  isFavorite?: boolean
}

export interface VacancyEntry {
  carparkNo: string
  vehicleType: string
  vacancy: number
  vacancyType?: string
  lastUpdateTime?: string
}

export interface VacancyMap {
  [carparkNo: string]: VacancyEntry[]
}

export interface CarparkListResponse {
  total: number
  carparks: CarparkInfo[]
}

export interface VacancyResponse {
  vacancies: VacancyMap
}

// ======== Favorite Types ========
export interface Favorite {
  id: number
  carpark_id: string
  carpark_name: string
  carpark_name_en: string
  district: string
  address: string
  latitude: number | null
  longitude: number | null
  created_at: string
}

export interface FavoritePayload {
  carpark_id: string
  carpark_name: string
  carpark_name_en?: string
  district?: string
  address?: string
  latitude?: number | null
  longitude?: number | null
}

// ======== API Response ========
export interface ApiError {
  message?: string
  detail?: string
  [key: string]: unknown
}
