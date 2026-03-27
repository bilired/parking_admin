<template>
  <div class="detail-panel">
    <div class="detail-header">
      <div class="detail-title-block">
        <h2 class="detail-name">{{ carpark.name }}</h2>
        <p v-if="carpark.nameEn" class="detail-name-en">{{ carpark.nameEn }}</p>
      </div>
      <div class="detail-header-actions">
        <el-button
          type="primary"
          :icon="Guide"
          size="small"
          @click="emit('navigate')"
        >
          導航
        </el-button>
        <el-button
          circle
          :type="isFavorite ? 'warning' : 'default'"
          :icon="isFavorite ? StarFilled : Star"
          size="small"
          @click="emit('toggle-favorite')"
        />
        <el-button
          circle
          text
          :icon="Close"
          size="small"
          class="close-btn"
          @click="emit('close')"
        />
      </div>
    </div>

    <div class="detail-body">
      <!-- Basic Info -->
      <div class="info-section">
        <div v-if="carpark.districtTc" class="info-row">
          <el-icon color="#4f8ef7"><Location /></el-icon>
          <span>{{ carpark.districtTc }}</span>
          <span v-if="carpark.districtEn" class="text-secondary"> · {{ carpark.districtEn }}</span>
        </div>
        <div v-if="carpark.addressTc" class="info-row">
          <el-icon color="#8b92a8"><OfficeBuilding /></el-icon>
          <span>{{ carpark.addressTc }}</span>
        </div>
        <div v-if="carpark.contactNo" class="info-row">
          <el-icon color="#8b92a8"><Phone /></el-icon>
          <a :href="`tel:${carpark.contactNo}`" class="link">{{ carpark.contactNo }}</a>
        </div>
        <div v-if="carpark.openingHours" class="info-row">
          <el-icon color="#8b92a8"><Clock /></el-icon>
          <span>{{ carpark.openingHours }}</span>
        </div>
        <div v-if="carpark.website" class="info-row">
          <el-icon color="#8b92a8"><Link /></el-icon>
          <a :href="carpark.website" target="_blank" rel="noopener" class="link">網站連結</a>
        </div>
      </div>

      <!-- Vacancy -->
      <div class="vacancy-section">
        <div class="section-title">
          <el-icon color="#4f8ef7"><Grid /></el-icon>
          實時空位
        </div>
        <div v-if="vacancy.length === 0" class="no-vacancy">
          <span>暫無空位數據</span>
        </div>
        <div v-else class="vacancy-grid">
          <div
            v-for="v in vacancy"
            :key="v.vehicleType"
            class="vacancy-item"
            :class="getVacancyClass(v.vacancy)"
          >
            <div class="vacancy-type">{{ getVehicleLabel(v.vehicleType) }}</div>
            <div class="vacancy-count">{{ v.vacancy ?? '-' }}</div>
            <div class="vacancy-label">空位</div>
          </div>
        </div>
        <div v-if="lastUpdate" class="update-time">
          <el-icon><Clock /></el-icon>
          更新時間：{{ lastUpdate }}
        </div>
      </div>

      <!-- Vehicle Types -->
      <div v-if="carpark.vehicleTypes && carpark.vehicleTypes.length" class="vehicle-section">
        <div class="section-title">
          <el-icon color="#4f8ef7"><Van /></el-icon>
          車輛類型
        </div>
        <div class="vehicle-tags">
          <el-tag
            v-for="vt in carpark.vehicleTypes"
            :key="vt.vehicleType"
            size="small"
            class="vehicle-tag"
          >
            {{ getVehicleLabel(vt.vehicleType) }}
          </el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Star, StarFilled, Close, Guide } from '@element-plus/icons-vue'
import type { CarparkInfo, VacancyEntry } from '@/types'

const props = defineProps<{
  carpark: CarparkInfo
  vacancy: VacancyEntry[]
  isFavorite: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'toggle-favorite'): void
  (e: 'navigate'): void
}>()

const lastUpdate = computed(() => {
  if (!props.vacancy.length) return ''
  return props.vacancy[0].lastUpdateTime ?? ''
})

function getVehicleLabel(type: string): string {
  const map: Record<string, string> = {
    P: '私家車',
    MC: '電單車',
    LGV: '輕型貨車',
    HGV: '重型貨車',
    CV: '商業車輛',
    COACH: '旅遊巴士',
  }
  return map[type] ?? type
}

function getVacancyClass(count: number): string {
  if (count === 0) return 'full'
  if (count < 10) return 'low'
  return 'available'
}
</script>

<style scoped>
.detail-panel {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  width: min(560px, calc(100% - 48px));
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
  z-index: 100;
  overflow: hidden;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 20px 16px;
  border-bottom: 1px solid var(--border);
  background: rgba(79, 142, 247, 0.05);
}

.detail-title-block { flex: 1; min-width: 0; }
.detail-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.3;
}
.detail-name-en {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.detail-header-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  margin-left: 12px;
}
.close-btn { color: var(--text-secondary) !important; }
.close-btn:hover { color: var(--text-primary) !important; }

.detail-body {
  padding: 16px 20px;
  max-height: 300px;
  overflow-y: auto;
}

.info-section { margin-bottom: 16px; }
.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-primary);
  padding: 4px 0;
}
.text-secondary { color: var(--text-secondary); }
.link { color: var(--accent); text-decoration: none; }
.link:hover { text-decoration: underline; }

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.vacancy-section { margin-bottom: 16px; }
.no-vacancy { font-size: 13px; color: var(--text-secondary); padding: 8px 0; }

.vacancy-grid {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.vacancy-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 16px;
  border-radius: 10px;
  min-width: 72px;
}
.vacancy-item.available { background: rgba(38, 194, 129, 0.12); border: 1px solid rgba(38, 194, 129, 0.3); }
.vacancy-item.low { background: rgba(245, 166, 35, 0.12); border: 1px solid rgba(245, 166, 35, 0.3); }
.vacancy-item.full { background: rgba(231, 76, 60, 0.12); border: 1px solid rgba(231, 76, 60, 0.3); }

.vacancy-type { font-size: 11px; color: var(--text-secondary); margin-bottom: 4px; }
.vacancy-count {
  font-size: 22px;
  font-weight: 700;
  line-height: 1;
}
.available .vacancy-count { color: #26c281; }
.low .vacancy-count { color: #f5a623; }
.full .vacancy-count { color: #e74c3c; }
.vacancy-label { font-size: 11px; color: var(--text-secondary); margin-top: 2px; }

.update-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-secondary);
}

.vehicle-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.vehicle-tag {
  background: rgba(79, 142, 247, 0.1) !important;
  border-color: rgba(79, 142, 247, 0.3) !important;
  color: var(--accent) !important;
}
</style>
