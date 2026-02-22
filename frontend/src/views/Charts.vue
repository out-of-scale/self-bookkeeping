<template>
  <div class="page-container" v-loading="loading">
    <div class="page-header">
      <h2 style="display:flex;align-items:center;"><Icon name="trending-up" size="24" /> 图表分析</h2>
      <p class="subtitle">深入了解消费习惯</p>
    </div>

    <!-- 月份选择 -->
    <div class="month-selector">
      <el-date-picker
        v-model="selectedMonthDate"
        type="month"
        format="YYYY年MM月"
        value-format="YYYY-MM"
        :clearable="false"
        class="elegant-date-picker"
        @change="handleMonthChange"
      >
        <template #prefix>
          <Icon name="calendar" size="18" style="color:var(--text-secondary); margin-right: 4px;" />
        </template>
      </el-date-picker>
    </div>

    <!-- 汇总卡片 -->
    <div class="grid-3" style="margin-bottom: 20px;">
      <div class="stat-card expense">
        <div class="label"><Icon name="dollar" size="16" /> 支出</div>
        <div class="value">¥{{ formatMoney(stats.total_expense) }}</div>
      </div>
      <div class="stat-card income">
        <div class="label"><Icon name="dollar" size="16" /> 收入</div>
        <div class="value">¥{{ formatMoney(stats.total_income) }}</div>
      </div>
      <div class="stat-card balance">
        <div class="label"><Icon name="bar-chart" size="16" /> 结余</div>
        <div class="value">¥{{ formatMoney(stats.balance) }}</div>
      </div>
    </div>

    <!-- 消费趋势折线图 -->
    <div class="chart-wrapper" style="margin-bottom: 16px;">
      <div class="chart-title"><Icon name="trending-up" /> 消费趋势</div>
      <LineChart v-if="stats.daily_expense.length > 0" :data="stats.daily_expense" :height="260" />
      <div v-else class="empty-state small"><div class="emoji">📈</div><div class="desc">暂无数据</div></div>
    </div>

    <!-- 支出构成 -->
    <div class="chart-wrapper">
      <div class="chart-title"><Icon name="pie-chart" /> 支出构成</div>
      <div v-if="stats.by_category.length > 0" class="category-bars">
        <div class="cat-row" v-for="(item, i) in stats.by_category" :key="item.category"
             :style="{ animationDelay: (i * 0.08) + 's' }">
          <div class="cat-left">
            <span class="cat-rank" :class="'top-' + (i + 1)">{{ i + 1 }}</span>
            <span class="cat-icon" :style="{ background: catBgColors[i % catBgColors.length] }">
              {{ getCategoryIcon(item.category) }}
            </span>
            <span class="cat-name">{{ item.category }}</span>
          </div>
          <div class="cat-right">
            <div class="cat-bar-track">
              <div class="cat-bar-fill" :style="{ '--w': item.percentage + '%', background: catColors[i % catColors.length], animationDelay: (i * 0.08 + 0.2) + 's' }"></div>
            </div>
            <span class="cat-amount">¥{{ formatMoney(item.amount) }}</span>
            <span class="cat-pct">{{ item.percentage }}%</span>
          </div>
        </div>
      </div>
      <div v-else class="empty-state small"><div class="emoji">📊</div><div class="desc">暂无数据</div></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getMonthStats } from '../api'
import LineChart from '../components/LineChart.vue'
import Icon from '../components/Icon.vue'

const catColors = ['#c2a383', '#d98880', '#82a88d', '#eab676', '#8eb1c7', '#d6bb9f', '#e09d8d', '#769b8b', '#a9a098']
const catBgColors = [
  'rgba(194,163,131,0.2)', 'rgba(217,136,128,0.2)', 'rgba(130,168,141,0.2)',
  'rgba(234,182,118,0.2)', 'rgba(142,177,199,0.2)', 'rgba(214,187,159,0.2)',
  'rgba(224,157,141,0.2)', 'rgba(118,155,139,0.2)', 'rgba(169,160,152,0.2)',
]

const loading = ref(true)
const today = new Date()
const currentYear = ref(today.getFullYear())
const currentMonth = ref(today.getMonth() + 1)

// 格式化为 'YYYY-MM'，以满足 DatePicker 的需求
const mm = String(currentMonth.value).padStart(2, '0')
const selectedMonthDate = ref(`${currentYear.value}-${mm}`)

function handleMonthChange(val) {
  if (val) {
    const [y, m] = val.split('-')
    currentYear.value = parseInt(y, 10)
    currentMonth.value = parseInt(m, 10)
    fetchData()
  }
}

const stats = ref({
  total_expense: 0, total_income: 0, balance: 0,
  by_category: [], daily_expense: [],
})

function formatMoney(n) {
  return Number(n || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const categoryIcons = {
  '餐饮': '🍜', '交通': '🚗', '购物': '🛍️', '娱乐': '🎮',
  '医疗': '🏥', '教育': '📚', '住房': '🏠', '通讯': '📱', '其他': '📦',
}
function getCategoryIcon(cat) { return categoryIcons[cat] || '📦' }

// 移除 prevMonth 和 nextMonth 函数，因为 DatePicker 自带控制

async function fetchData() {
  loading.value = true
  try {
    const res = await getMonthStats(currentYear.value, currentMonth.value)
    stats.value = res.data
  } catch (e) {
    console.error('Failed to load chart data:', e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.month-selector {
  display: flex; align-items: center; justify-content: center; margin-bottom: 24px;
}
:deep(.elegant-date-picker) {
  width: 160px !important;
}
:deep(.elegant-date-picker .el-input__wrapper) {
  background: var(--bg-card) !important;
  border-radius: 12px !important;
  border: 1px solid var(--border-color) !important;
  box-shadow: var(--shadow-sm) !important;
  padding: 8px 12px !important;
  cursor: pointer !important;
  transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
}
:deep(.elegant-date-picker .el-input__wrapper:hover) {
  border-color: var(--primary-light) !important;
  box-shadow: var(--shadow-md) !important;
  transform: translateY(-2px);
}
:deep(.elegant-date-picker .el-input__inner) {
  font-size: 18px !important;
  font-weight: 700 !important;
  color: var(--text-primary) !important;
  font-variant-numeric: tabular-nums;
  cursor: pointer !important;
  text-align: center !important;
  padding: 0 !important;
}

/* 分类条形图 */
.category-bars { display: flex; flex-direction: column; gap: 14px; }
.cat-row {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  animation: catRowIn 0.4s ease both;
}
.cat-left { display: flex; align-items: center; gap: 8px; min-width: 80px; }
.cat-rank {
  width: 22px; height: 22px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; background: var(--bg-primary); color: var(--text-secondary);
}
.top-1 { background: linear-gradient(135deg, #f59e0b, #f97316); color: #fff; }
.top-2 { background: linear-gradient(135deg, #94a3b8, #cbd5e1); color: #1e293b; }
.top-3 { background: linear-gradient(135deg, #b45309, #d97706); color: #fff; }
.cat-icon {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.cat-name { font-size: 14px; font-weight: 500; white-space: nowrap; }
.cat-right { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; }
.cat-bar-track {
  flex: 1; height: 8px; border-radius: 4px;
  background: var(--bg-primary); overflow: hidden;
}
.cat-bar-fill {
  height: 100%; border-radius: 4px;
  width: 0;
  animation: barGrow 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}
.cat-amount {
  font-size: 14px; font-weight: 600; color: var(--text-primary);
  min-width: 72px; text-align: right; white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.cat-pct { font-size: 12px; color: var(--text-muted); min-width: 36px; text-align: right; }
.empty-state.small { padding: 40px 20px; }

@keyframes catRowIn {
  from { opacity: 0; transform: translateX(-12px); }
  to { opacity: 1; transform: translateX(0); }
}
@keyframes barGrow {
  from { width: 0; }
  to { width: var(--w, 100%); }
}
</style>

