<template>
  <div class="favorites-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-button
          circle
          text
          :icon="ArrowLeft"
          class="back-btn"
          @click="$router.push('/')"
        />
        <div class="header-title">
          <el-icon :size="20" color="#4f8ef7"><Star /></el-icon>
          <span>我的收藏</span>
        </div>
      </div>
      <div class="header-right">
        <span class="total-count">
          共 <strong>{{ carparkStore.favorites.length }}</strong> 個
        </span>
      </div>
    </div>

    <!-- Content -->
    <div class="page-content" v-loading="loading">
      <template v-if="!loading">
        <div v-if="carparkStore.favorites.length === 0" class="empty-state">
          <el-icon :size="80" color="#2a2f45"><Star /></el-icon>
          <h3>尚無收藏</h3>
          <p>在地圖上點擊停車場，然後點擊星號即可收藏</p>
          <el-button type="primary" @click="$router.push('/')">
            <el-icon><Search /></el-icon> 搜索停車場
          </el-button>
        </div>

        <div v-else class="favorites-grid">
          <div
            v-for="fav in carparkStore.favorites"
            :key="fav.id"
            class="fav-card"
          >
            <div class="fav-card-header">
              <div class="fav-name">
                <h3>{{ fav.carpark_name }}</h3>
                <p v-if="fav.carpark_name_en" class="name-en">{{ fav.carpark_name_en }}</p>
              </div>
              <el-button
                circle
                text
                :icon="Delete"
                class="delete-btn"
                @click="handleRemove(fav)"
              />
            </div>
            <div class="fav-card-body">
              <div v-if="fav.district" class="info-tag">
                <el-icon><Location /></el-icon>
                {{ fav.district }}
              </div>
              <div v-if="fav.address" class="info-address">
                {{ fav.address }}
              </div>
            </div>
            <div class="fav-card-footer">
              <span class="added-time">
                <el-icon><Clock /></el-icon>
                {{ formatDate(fav.created_at) }}
              </span>
              <el-button
                size="small"
                type="primary"
                plain
                class="view-map-btn"
                @click="goToMap(fav)"
              >
                <el-icon><MapLocation /></el-icon> 在地圖查看
              </el-button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Star, Delete, Search, Clock, MapLocation } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useCarparkStore } from '@/stores/carpark'
import type { Favorite } from '@/types'

const router = useRouter()
const carparkStore = useCarparkStore()
const loading = ref(false)

async function handleRemove(fav: Favorite) {
  await ElMessageBox.confirm(`確定取消收藏「${fav.carpark_name}」？`, '提示', { type: 'warning' })
  try {
    await carparkStore.removeFavorite(fav.carpark_id)
    ElMessage.success('已取消收藏')
  } catch {
    ElMessage.error('操作失敗')
  }
}

function goToMap(fav: Favorite) {
  // Navigate to home and select the carpark
  router.push({ path: '/', query: { highlight: fav.carpark_id } })
}

function formatDate(dateStr: string) {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

onMounted(async () => {
  loading.value = true
  try {
    await carparkStore.fetchFavorites()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.favorites-page {
  min-height: 100vh;
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 28px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.back-btn { color: var(--text-secondary) !important; }
.back-btn:hover { color: var(--accent) !important; }

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.total-count {
  font-size: 14px;
  color: var(--text-secondary);
}
.total-count strong { color: var(--accent); }

.page-content {
  flex: 1;
  padding: 28px;
  overflow-y: auto;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 16px;
  text-align: center;
}
.empty-state h3 {
  font-size: 20px;
  color: var(--text-primary);
}
.empty-state p {
  font-size: 14px;
  color: var(--text-secondary);
  max-width: 300px;
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.fav-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.fav-card:hover {
  border-color: var(--accent);
  box-shadow: 0 4px 20px rgba(79, 142, 247, 0.12);
}

.fav-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}
.fav-name h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}
.name-en {
  font-size: 12px;
  color: var(--text-secondary);
}
.delete-btn { color: var(--text-secondary) !important; }
.delete-btn:hover { color: var(--accent-danger) !important; }

.fav-card-body { margin-bottom: 16px; }

.info-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--accent);
  background: rgba(79, 142, 247, 0.12);
  padding: 4px 10px;
  border-radius: 20px;
  margin-bottom: 8px;
}
.info-address {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.fav-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--border);
  padding-top: 12px;
}
.added-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.view-map-btn {
  color: #ffffff !important;
}

.view-map-btn:hover,
.view-map-btn:focus {
  color: #ffffff !important;
}
</style>
