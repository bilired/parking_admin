<template>
  <div
    class="carpark-card"
    :class="{ selected }"
    @click="emit('click')"
  >
    <div class="card-main">
      <div class="card-info">
        <div class="carpark-name-row">
          <span v-if="isFavorite" class="favorite-badge" aria-label="已收藏">
            <el-icon><StarFilled /></el-icon>
          </span>
          <div class="carpark-name">{{ carpark.name }}</div>
        </div>
        <div v-if="carpark.nameEn" class="carpark-name-en">{{ carpark.nameEn }}</div>
        <div class="carpark-meta">
          <span v-if="carpark.districtTc" class="meta-tag">
            <el-icon><Location /></el-icon>
            {{ carpark.districtTc }}
          </span>
        </div>
      </div>
      <div class="card-right">
        <div class="vacancy-badge" :class="vacancyClass">
          <span v-if="vacancy !== null">{{ vacancy }}</span>
          <span v-else class="na">無數據</span>
        </div>
        <el-icon
          class="fav-icon"
          :class="{ 'is-fav': isFavorite }"
          @click.stop="emit('toggle-favorite')"
        >
          <StarFilled v-if="isFavorite" />
          <Star v-else />
        </el-icon>
      </div>
    </div>
    <div v-if="carpark.addressTc" class="card-address">
      {{ carpark.addressTc }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Star, StarFilled } from '@element-plus/icons-vue'
import type { CarparkInfo } from '@/types'

const props = defineProps<{
  carpark: CarparkInfo
  vacancy: number | null
  selected: boolean
  isFavorite: boolean
}>()

const emit = defineEmits<{
  (e: 'click'): void
  (e: 'toggle-favorite'): void
}>()

const vacancyClass = computed(() => {
  if (props.vacancy === null) return 'unknown'
  if (props.vacancy === 0) return 'full'
  if (props.vacancy < 10) return 'low'
  return 'available'
})
</script>

<style scoped>
.carpark-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.carpark-card:hover {
  border-color: rgba(79, 142, 247, 0.5);
  background: rgba(79, 142, 247, 0.06);
  box-shadow: 0 2px 12px rgba(79, 142, 247, 0.08);
}
.carpark-card.selected {
  border-color: var(--accent);
  background: rgba(79, 142, 247, 0.08);
  box-shadow: 0 0 0 1px var(--accent);
}

.card-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.card-info { flex: 1; min-width: 0; }
.carpark-name-row {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}
.carpark-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.favorite-badge {
  width: 22px;
  height: 22px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #d89b34;
  color: #ffffff;
  box-shadow: 0 4px 10px rgba(216, 155, 52, 0.35);
  flex-shrink: 0;
}
.favorite-badge .el-icon {
  font-size: 12px;
}
.carpark-name-en {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 1px;
}
.carpark-meta { margin-top: 6px; }
.meta-tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  color: var(--accent);
  background: rgba(79, 142, 247, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
}

.card-right {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.vacancy-badge {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 700;
}
.vacancy-badge.available { background: rgba(38, 194, 129, 0.15); color: #26c281; }
.vacancy-badge.low { background: rgba(245, 166, 35, 0.15); color: #f5a623; }
.vacancy-badge.full { background: rgba(231, 76, 60, 0.15); color: #e74c3c; }
.vacancy-badge.unknown { background: rgba(139, 146, 168, 0.1); color: var(--text-secondary); }
.vacancy-badge .na {
  font-size: 11px;
  font-weight: 600;
  line-height: 1.2;
  text-align: center;
  padding: 0 4px;
}

.fav-icon {
  font-size: 18px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color 0.2s, transform 0.2s;
}
.fav-icon:hover { transform: scale(1.2); color: #f5a623; }
.fav-icon.is-fav { color: #f5a623; }

.card-address {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
