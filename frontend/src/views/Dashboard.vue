<template>
  <div class="page-container" v-loading="loading">
    <div class="page-header">
      <h2>📊 本月概况</h2>
      <p class="subtitle">{{ currentMonthLabel }}</p>
    </div>

    <!-- 资产总览卡片 (新增) -->
    <div class="net-worth-card" @click="showNetWorthDialog = true">
      <div class="nw-label">💰 总净资产 <span class="edit-icon">✏️</span></div>
      <div class="nw-value">¥{{ formatMoney(netWorth.net_worth) }}</div>
      <div class="nw-desc" v-if="netWorth.base_worth">包含初始设定的 ¥{{ formatMoney(netWorth.base_worth) }}</div>
      <div class="nw-desc" v-else>点击设定此刻的所有存款总计</div>
    </div>

    <!-- 三卡片汇总 -->
    <div class="grid-3">
      <div class="stat-card expense">
        <div class="label">💸 总支出</div>
        <div class="value">¥{{ formatMoney(stats.total_expense) }}</div>
      </div>
      <div class="stat-card income">
        <div class="label">💰 总收入</div>
        <div class="value">¥{{ formatMoney(stats.total_income) }}</div>
      </div>
      <div class="stat-card balance">
        <div class="label">📈 结余</div>
        <div class="value" :class="{ negative: stats.balance < 0 }">¥{{ formatMoney(stats.balance) }}</div>
      </div>
    </div>

    <!-- 图表区域 -->
    <!-- 支出分类 -->
    <div class="chart-wrapper">
      <div class="chart-title">🏷️ 支出分类</div>
      <div v-if="stats.by_category.length > 0" class="category-bars">
        <div class="cat-row" v-for="(item, i) in stats.by_category" :key="item.category"
             :style="{ animationDelay: (i * 0.08) + 's' }">
          <div class="cat-left">
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
          </div>
        </div>
      </div>
      <div v-else class="empty-state small"><div class="emoji">📊</div><div class="desc">暂无支出</div></div>
    </div>

    <!-- 每日支出 -->
    <div class="chart-wrapper">
      <div class="chart-title">📊 每日支出</div>
      <BarChart v-if="stats.daily_expense.length > 0" :data="stats.daily_expense" />
      <div v-else class="empty-state small"><div class="emoji">📅</div><div class="desc">暂无数据</div></div>
    </div>

    <!-- 最近交易 -->
    <div class="chart-wrapper">
      <div class="chart-title" style="display:flex;justify-content:space-between;align-items:center;">
        <span>📝 最近交易</span>
        <router-link to="/records" class="view-all-btn">查看全部 →</router-link>
      </div>
      <div v-if="receipts.length > 0">
        <div class="transaction-item" v-for="item in receipts" :key="item.id">
          <div class="info">
            <div class="category-icon" :style="{ background: getCategoryColor(item.category) }">
              {{ getCategoryIcon(item.category) }}
            </div>
            <div>
              <div class="merchant">{{ item.merchant }}</div>
              <div class="date">{{ formatDate(item.date) }} · {{ item.category }}</div>
            </div>
          </div>
          <div class="amount" :class="item.type">
            {{ item.type === 'expense' ? '-' : '+' }}¥{{ formatMoney(item.amount) }}
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <div class="emoji">📭</div>
        <div class="title">暂无交易记录</div>
        <div class="desc">使用 iPhone 快捷指令上传支付截图开始记账</div>
      </div>
    </div>

    <!-- 净资产校准弹窗 (新增) -->
    <el-dialog v-model="showNetWorthDialog" title="核对资产" width="90%" custom-class="mobile-dialog">
      <div class="dialog-tip">请计算您目前所有银行卡、微信、支付宝的余额总和，并填入下方。系统会自动反推并记录账本的误差。</div>
      <el-input 
        v-model="inputNetWorth" 
        type="number" 
        placeholder="例如: 56000.00"
        size="large">
        <template #prepend>¥</template>
      </el-input>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showNetWorthDialog = false">取消</el-button>
          <el-button type="primary" @click="submitNetWorth" :loading="savingNetWorth">保存校准</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getMonthStats, getReceipts, getNetWorth, updateNetWorth } from '../api'
import { ElMessage } from 'element-plus'
import BarChart from '../components/BarChart.vue'

const loading = ref(true)
const stats = ref({
  total_expense: 0, total_income: 0, balance: 0,
  by_category: [], daily_expense: [],
})
const receipts = ref([])

// 资产相关
const netWorth = ref({ net_worth: 0, base_worth: 0 })
const showNetWorthDialog = ref(false)
const inputNetWorth = ref('')
const savingNetWorth = ref(false)

const today = new Date()
const currentMonthLabel = computed(() => `${today.getFullYear()}年${today.getMonth() + 1}月`)

function formatMoney(n) {
  if (n === undefined || n === null) return '0.00'
  return Number(n).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  return `${parseInt(parts[1])}月${parseInt(parts[2])}日`
}

const categoryIcons = {
  '餐饮': '🍜', '交通': '🚗', '购物': '🛍️', '娱乐': '🎮',
  '医疗': '🏥', '教育': '📚', '住房': '🏠', '通讯': '📱', '其他': '📦',
}
const catColors = ['#6366f1', '#f43f5e', '#10b981', '#f59e0b', '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6', '#64748b']
const catBgColors = [
  'rgba(99,102,241,0.2)', 'rgba(244,63,94,0.2)', 'rgba(16,185,129,0.2)',
  'rgba(245,158,11,0.2)', 'rgba(59,130,246,0.2)', 'rgba(139,92,246,0.2)',
  'rgba(236,72,153,0.2)', 'rgba(20,184,166,0.2)', 'rgba(100,116,139,0.2)',
]
const categoryColors = {
  '餐饮': 'rgba(99,102,241,0.2)', '交通': 'rgba(59,130,246,0.2)', '购物': 'rgba(244,63,94,0.2)',
  '娱乐': 'rgba(139,92,246,0.2)', '医疗': 'rgba(16,185,129,0.2)', '教育': 'rgba(245,158,11,0.2)',
  '住房': 'rgba(20,184,166,0.2)', '通讯': 'rgba(236,72,153,0.2)', '其他': 'rgba(100,116,139,0.2)',
}
function getCategoryIcon(cat) { return categoryIcons[cat] || '📦' }
function getCategoryColor(cat) { return categoryColors[cat] || 'rgba(100,116,139,0.2)' }

onMounted(async () => {
  try {
    const [statsRes, receiptsRes, netWorthRes] = await Promise.all([
      getMonthStats(today.getFullYear(), today.getMonth() + 1),
      getReceipts({ page: 1, page_size: 10 }),
      getNetWorth()
    ])
    stats.value = statsRes.data
    receipts.value = receiptsRes.data.items
    netWorth.value = netWorthRes.data
    inputNetWorth.value = netWorthRes.data.net_worth
  } catch (e) {
    console.error('Failed to load dashboard data:', e)
  } finally {
    loading.value = false
  }
})

async function submitNetWorth() {
  if (!inputNetWorth.value) {
    ElMessage.warning('请输入当前总资产金额')
    return
  }
  savingNetWorth.value = true
  try {
    const res = await updateNetWorth(Number(inputNetWorth.value))
    netWorth.value = res.data
    ElMessage.success('资产校准成功！')
    showNetWorthDialog.value = false
  } catch (e) {
    ElMessage.error('校准失败：' + (e.response?.data?.detail || e.message))
  } finally {
    savingNetWorth.value = false
  }
}
</script>

<style scoped>
.view-all-btn {
  color: var(--primary-light);
  font-size: 13px;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}
.view-all-btn:hover { color: var(--primary); }
.empty-state.small { padding: 40px 20px; }
.negative { color: #f87171 !important; }

/* 净资产卡片 */
.net-worth-card {
  background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  color: white;
  box-shadow: 0 8px 16px -4px rgba(79, 70, 229, 0.4);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.net-worth-card:active {
  transform: scale(0.98);
}
.nw-label {
  font-size: 14px;
  opacity: 0.9;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}
.edit-icon {
  font-size: 12px;
  opacity: 0.6;
}
.nw-value {
  font-size: 36px;
  font-weight: 700;
  margin: 8px 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
  font-variant-numeric: tabular-nums;
}
.nw-desc {
  font-size: 12px;
  opacity: 0.75;
}

/* 弹窗底部提示 */
.dialog-tip {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;
  line-height: 1.5;
}

/* 分类条形图 */
.category-bars { display: flex; flex-direction: column; gap: 14px; }
.cat-row {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  animation: catRowIn 0.4s ease both;
}
.cat-left { display: flex; align-items: center; gap: 8px; min-width: 72px; }
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

@keyframes catRowIn {
  from { opacity: 0; transform: translateX(-12px); }
  to { opacity: 1; transform: translateX(0); }
}
@keyframes barGrow {
  from { width: 0; }
  to { width: var(--w, 100%); }
}
</style>
