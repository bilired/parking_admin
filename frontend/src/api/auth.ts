import request from './request'
import type { LoginPayload, RegisterPayload, AuthResponse, User } from '@/types'

export const authApi = {
  login(data: LoginPayload) {
    return request.post<AuthResponse>('/auth/login/', data)
  },
  register(data: RegisterPayload) {
    return request.post<AuthResponse>('/auth/register/', data)
  },
  logout(refresh: string) {
    return request.post('/auth/logout/', { refresh })
  },
  me() {
    return request.get<User>('/auth/me/')
  },
  updateProfile(data: Partial<User>) {
    return request.patch<User>('/auth/profile/', data)
  },
}
