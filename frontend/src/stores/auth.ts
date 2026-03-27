import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User, LoginPayload, RegisterPayload } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  const isLoggedIn = computed(() => !!accessToken.value && !!user.value)

  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  function clearTokens() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function login(payload: LoginPayload) {
    const { data } = await authApi.login(payload)
    setTokens(data.access, data.refresh)
    user.value = data.user
    return data
  }

  async function register(payload: RegisterPayload) {
    const { data } = await authApi.register(payload)
    setTokens(data.access, data.refresh)
    user.value = data.user
    return data
  }

  async function logout() {
    if (refreshToken.value) {
      try {
        await authApi.logout(refreshToken.value)
      } catch {
        // ignore errors during logout
      }
    }
    clearTokens()
  }

  async function fetchMe() {
    try {
      const { data } = await authApi.me()
      user.value = data
    } catch {
      clearTokens()
    }
  }

  // On app start, restore user if token exists
  async function init() {
    if (accessToken.value && !user.value) {
      await fetchMe()
    }
  }

  return { user, accessToken, isLoggedIn, login, register, logout, fetchMe, init }
})
