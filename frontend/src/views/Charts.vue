<template>
  <div class="page-container" v-loading="loading">
    <div class="page-header">
      <h2>📈 图表分析</h2>
      <p class="subtitle">深入了解消费习惯</p>
    </div>

    <!-- 月份选择 -->
    <div class="month-selector">
      <button class="month-btn" @click="prevMonth">◀</button>
      <span class="month-label">{{ displayMonth }}</span>
      <button class="month-btn" @click="nextMonth">▶</button>
    </div>

    <!-- 汇总卡片 -->
    <div class="grid-3" style="margin-bottom: 20px;">
      <div class="stat-card expense">
        <div class="label">💸 支出</div>
        <div class="value">¥{{ formatMoney(stats.total_expense) }}</div>
      </div>
      <div class="stat-card income">
        <div class="label">💰 收入</div>
        <div class="value">¥{{ formatMoney(stats.total_income) }}</div>
      </div>
      <div class="stat-card balance">
        <div class="label">📊 结余</div>
        <div class="value">¥{{ formatMoney(stats.balance) }}</div>
      </div>
    </div>

    <!-- 消费趋势折线图 -->
    <div class="chart-wrapper" style="margin-bottom: 16px;">
      <div class="chart-title">📈 消费趋势</div>
      <LineChart v-if="stats.daily_expense.length > 0" :data="stats.daily_expense" :height="260" />
      <div v-else class="empty-state small"><div class="emoji">📈</div><div class="desc">暂无数据</div></div>
    </div>

    <!-- 支出构成 -->
    <div class="chart-wrapper">
      <div class="chart-title">🏷️ 支出构成</div>
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

const catColors = ['#6366f1', '#f43f5e', '#10b981', '#f59e0b', '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6', '#64748b']
const catBgColors = [
  'rgba(99,102,241,0.2)', 'rgba(244,63,94,0.2)', 'rgba(16,185,129,0.2)',
  'rgba(245,158,11,0.2)', 'rgba(59,130,246,0.2)', 'rgba(139,92,246,0.2)',
  'rgba(236,72,153,0.2)', 'rgba(20,184,166,0.2)', 'rgba(100,116,139,0.2)',
]

const loading = ref(true)
const today = new Date()
const currentYear = ref(today.getFullYear())
const currentMonth = ref(today.getMonth() + 1)

const displayMonth = computed(() => `${currentYear.value}年${currentMonth.value}月`)

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

function prevMonth() {
  currentMonth.value--
  if (currentMonth.value < 1) { currentMonth.value = 12; currentYear.value-- }
  fetchData()
}

function nextMonth() {
  currentMonth.value++
  if (currentMonth.value > 12) { currentMonth.value = 1; currentYear.value++ }
  fetchData()
}

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
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}
.month-btn {
  width: 30px; height: 30px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: color 0.15s;
}
.month-btn:hover { color: var(--primary); border-color: var(--primary); }
.month-label { font-size: 16px; font-weight: 600; color: var(--text-primary); }

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

