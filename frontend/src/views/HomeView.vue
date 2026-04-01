<template>
  <div class="home-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <!-- Header -->
      <div class="sidebar-header">
        <div class="logo">
          <img src="/hk-emblem.png" alt="香港區旗紫荊花" class="sidebar-emblem" />
          <span v-show="!sidebarCollapsed">香港停車場</span>
        </div>
        <div class="header-actions">
          <el-tooltip v-if="sidebarCollapsed" content="展開側欄">
            <el-button
              circle
              text
              :icon="Expand"
              class="icon-btn sidebar-expand-btn"
              @click="expandSidebar"
            />
          </el-tooltip>
          <el-tooltip v-else content="收起側欄">
            <el-button
              circle
              text
              :icon="Fold"
              class="icon-btn"
              @click="toggleSidebar"
            />
          </el-tooltip>
          <el-tooltip v-if="sidebarCollapsed" content="切換搜索浮層">
            <el-button
              circle
              text
              :icon="Search"
              class="icon-btn"
              @click="toggleSidebar"
            />
          </el-tooltip>
          <el-tooltip content="收藏清單">
            <el-button
              circle
              text
              :icon="Star"
              class="icon-btn"
              @click="$router.push('/favorites')"
            />
          </el-tooltip>
          <el-dropdown v-show="!sidebarCollapsed" @command="handleUserCmd">
            <el-avatar :size="32" class="user-avatar">
              {{ authStore.user?.username?.charAt(0).toUpperCase() }}
            </el-avatar>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  <el-icon><User /></el-icon> {{ authStore.user?.username }}
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon> 登出
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- Search -->
      <div v-show="!sidebarCollapsed" class="search-area">
        <el-input
          v-model="searchText"
          placeholder="搜索停車場名稱或地址..."
          prefix-icon="Search"
          clearable
          @input="debouncedSearch"
          @clear="debouncedSearch"
        />
        <el-select
          v-model="selectedDistrict"
          placeholder="選擇地區"
          clearable
          style="width: 100%; margin-top: 10px"
          @change="handleSearch"
        >
          <el-option
            v-for="d in carparkStore.districts"
            :key="d"
            :label="d"
            :value="d"
          />
        </el-select>
      </div>

      <!-- Stats -->
      <div v-show="!sidebarCollapsed" class="stats-bar">
        <span class="stats-count">
          找到 <strong>{{ carparkStore.total }}</strong> 個停車場
        </span>
        <el-button
          size="small"
          text
          :loading="vacancyLoading"
          @click="refreshVacancy"
        >
          <el-icon><Refresh /></el-icon> 更新空位
        </el-button>
      </div>

      <!-- Carpark List -->
      <div v-show="!sidebarCollapsed" class="carpark-list" v-loading="carparkStore.loading">
        <div
          v-if="!carparkStore.loading && carparkStore.carparks.length === 0"
          class="empty-state"
        >
          <el-icon :size="48" color="#8b92a8"><OfficeBuilding /></el-icon>
          <p>未找到停車場</p>
        </div>
        <CarparkCard
          v-for="cp in carparkStore.carparks"
          :key="cp.carparkNo"
          :carpark="cp"
          :vacancy="carparkStore.getVacancySummary(cp.carparkNo)"
          :selected="carparkStore.selectedCarpark?.carparkNo === cp.carparkNo"
          :is-favorite="carparkStore.isFavorite(cp.carparkNo)"
          @click="handleSelectCarpark(cp)"
          @toggle-favorite="handleToggleFavorite(cp)"
        />
      </div>
    </aside>

    <!-- Map Area -->
    <main class="map-area">
      <transition name="search-panel">
        <div v-if="showFloatingSearch" class="floating-search-panel">
          <div class="floating-search-header">
            <span>搜索停車場</span>
            <el-button
              circle
              text
              :icon="Close"
              class="icon-btn"
              @click="showFloatingSearch = false"
            />
          </div>
          <el-input
            v-model="searchText"
            placeholder="搜索停車場名稱或地址..."
            prefix-icon="Search"
            clearable
            @input="debouncedSearch"
            @clear="debouncedSearch"
          />
          <el-select
            v-model="selectedDistrict"
            placeholder="選擇地區"
            clearable
            class="floating-search-select"
            @change="handleSearch"
          >
            <el-option
              v-for="d in carparkStore.districts"
              :key="d"
              :label="d"
              :value="d"
            />
          </el-select>
        </div>
      </transition>
      <MapboxMap
        :carparks="carparkStore.carparks"
        :selected-carpark="carparkStore.selectedCarpark"
        :vacancy-map="carparkStore.vacancyMap"
        :favorite-ids="carparkStore.favorites.map((f) => f.carpark_id)"
        :sidebar-collapsed="sidebarCollapsed"
        :route-target="routeTarget"
        :route-request-id="routeRequestId"
        @select="handleSelectCarpark"
      />
      <!-- Detail Panel -->
      <transition name="slide-up">
        <CarparkDetail
          v-if="carparkStore.selectedCarpark"
          :carpark="carparkStore.selectedCarpark"
          :vacancy="carparkStore.vacancyMap[carparkStore.selectedCarpark.carparkNo] ?? []"
          :is-favorite="carparkStore.isFavorite(carparkStore.selectedCarpark.carparkNo)"
          @close="carparkStore.selectCarpark(null)"
          @navigate="handleNavigate(carparkStore.selectedCarpark!)"
          @toggle-favorite="handleToggleFavorite(carparkStore.selectedCarpark!)"
          @live="handleLive(carparkStore.selectedCarpark!)"
        />
      </transition>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Star, Refresh, Fold, Expand, Search, Close } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useCarparkStore } from '@/stores/carpark'
import CarparkCard from '@/components/CarparkCard.vue'
import CarparkDetail from '@/components/CarparkDetail.vue'
import MapboxMap from '@/components/MapboxMap.vue'
import type { CarparkInfo } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const carparkStore = useCarparkStore()

const searchText = ref('')
const selectedDistrict = ref('')
const vacancyLoading = ref(false)
const sidebarCollapsed = ref(false)
const showFloatingSearch = ref(false)
const routeTarget = ref<CarparkInfo | null>(null)
const routeRequestId = ref(0)

let searchTimer: ReturnType<typeof setTimeout> | null = null

function debouncedSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(handleSearch, 400)
}

function toggleSidebar() {
  if (sidebarCollapsed.value) {
    showFloatingSearch.value = !showFloatingSearch.value
    return
  }

  sidebarCollapsed.value = true
  showFloatingSearch.value = false
}

function expandSidebar() {
  sidebarCollapsed.value = false
  showFloatingSearch.value = false
}

function handleNavigate(cp: CarparkInfo) {
  routeTarget.value = cp
  routeRequestId.value += 1
}



async function handleSearch() {
  await carparkStore.fetchCarparks({
    search: searchText.value || undefined,
    district: selectedDistrict.value || undefined,
  })
}

async function refreshVacancy() {
  vacancyLoading.value = true
  try {
    const ids = carparkStore.carparks.map((c) => c.carparkNo).slice(0, 100)
    await carparkStore.fetchVacancy(ids)
  } catch {
    ElMessage.warning('無法獲取最新空位資料')
  } finally {
    vacancyLoading.value = false
  }
}

function handleSelectCarpark(cp: CarparkInfo) {
  carparkStore.selectCarpark(cp)
}

async function handleToggleFavorite(cp: CarparkInfo) {
  if (!cp) return
  try {
    if (carparkStore.isFavorite(cp.carparkNo)) {
      await carparkStore.removeFavorite(cp.carparkNo)
      ElMessage.success('已取消收藏')
    } else {
      await carparkStore.addFavorite({
        carpark_id: cp.carparkNo,
        carpark_name: cp.name,
        carpark_name_en: cp.nameEn ?? '',
        district: cp.districtTc ?? '',
        address: cp.addressTc ?? '',
        latitude: cp.latitude ?? null,
        longitude: cp.longitude ?? null,
      })
      ElMessage.success('已加入收藏')
    }
  } catch {
    ElMessage.error('操作失敗，請稍後再試')
  }
}

async function handleLive(cp: CarparkInfo) {
  if (!cp || cp.longitude == null || cp.latitude == null) {
    ElMessage.warning('此停車場沒有可用座標，無法開啟實況')
    return
  }
  const url = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${cp.latitude},${cp.longitude}`
  const newWindow = window.open(url, '_blank', 'noopener,noreferrer')
  if (!newWindow) {
    ElMessage.warning('無法開啟街景視窗，請檢查瀏覽器彈出視窗設定')
  }
}

async function handleUserCmd(cmd: string) {
  if (cmd === 'logout') {
    await ElMessageBox.confirm('確定要登出嗎？', '提示', { type: 'warning' })
    await authStore.logout()
    router.push('/login')
  }
}

onMounted(async () => {
  await Promise.all([
    carparkStore.fetchCarparks(),
    carparkStore.fetchDistricts(),
    carparkStore.fetchFavorites(),
  ])
  // Initial vacancy fetch for visible carparks
  if (carparkStore.carparks.length > 0) {
    refreshVacancy()
  }
  // Handle highlight query param (coming from Favorites page)
  const highlightId = route.query.highlight as string | undefined
  if (highlightId) {
    const cp = carparkStore.carparks.find((c) => c.carparkNo === highlightId)
    if (cp) carparkStore.selectCarpark(cp)
  }
})

watch(sidebarCollapsed, (collapsed) => {
  if (!collapsed) {
    showFloatingSearch.value = false
  }
})
</script>

<style scoped>
.home-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-primary);
}

/* Sidebar */
.sidebar {
  width: 380px;
  min-width: 340px;
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  z-index: 10;
  transition: width 0.28s ease, min-width 0.28s ease;
}

.sidebar.collapsed {
  width: 72px;
  min-width: 72px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.sidebar.collapsed .sidebar-header {
  padding: 16px 12px;
  flex-direction: column;
  gap: 12px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
}

.sidebar-emblem {
  width: 22px;
  height: 22px;
  object-fit: contain;
  border-radius: 5px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sidebar.collapsed .header-actions {
  flex-direction: column;
}

.icon-btn {
  color: var(--text-secondary) !important;
  font-size: 18px;
}
.icon-btn:hover { color: var(--accent) !important; }

.sidebar.collapsed .sidebar-expand-btn {
  color: #ffffff !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

.sidebar.collapsed .sidebar-expand-btn:hover {
  color: #ffffff !important;
  background: rgba(255, 255, 255, 0.08) !important;
  border: none !important;
  box-shadow: none !important;
}

.user-avatar {
  background: var(--accent);
  color: #fff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

.search-area {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.stats-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.stats-count {
  font-size: 13px;
  color: var(--text-secondary);
}
.stats-count strong { color: var(--accent); }

.carpark-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  gap: 12px;
  font-size: 14px;
}

/* Map Area */
.map-area {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.floating-search-panel {
  position: absolute;
  top: 72px;
  left: 16px;
  z-index: 35;
  width: min(320px, calc(100vw - 32px));
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid var(--border);
  border-radius: 18px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.16);
  backdrop-filter: blur(14px);
}

.floating-search-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 700;
}

.floating-search-select {
  width: 100%;
}

.search-panel-enter-active,
.search-panel-leave-active {
  transition: opacity 0.24s ease, transform 0.24s ease;
}

.search-panel-enter-from,
.search-panel-leave-to {
  opacity: 0;
  transform: translateX(-18px);
}

/* Detail Panel transition */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

:deep(.el-loading-mask) {
  background-color: rgba(245, 251, 255, 0.82) !important;
}

@media (max-width: 768px) {
  .floating-search-panel {
    top: 16px;
    left: 16px;
    width: min(320px, calc(100vw - 32px));
  }
}
</style>
