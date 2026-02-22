<template>
  <div class="page-container" v-loading="loading">
    <div class="page-header">
      <h2 style="display:flex;align-items:center;"><Icon name="calendar" size="24" /> 年度账单</h2>
      <p class="subtitle">{{ selectedYear }}年收支概览</p>
    </div>

    <!-- 年份选择 -->
    <div class="month-selector">
      <el-date-picker
        v-model="selectedYearDate"
        type="year"
        format="YYYY年"
        value-format="YYYY"
        :clearable="false"
        class="elegant-date-picker"
        @change="handleYearChange"
      >
        <template #prefix>
          <Icon name="calendar" size="18" style="color:var(--text-secondary); margin-right: 4px;" />
        </template>
      </el-date-picker>
    </div>

    <!-- 年度汇总卡片 -->
    <div class="grid-3">
      <div class="stat-card expense">
        <div class="label"><Icon name="dollar" size="16" /> 年度总支出</div>
        <div class="value">¥{{ formatMoney(yearTotalExpense) }}</div>
      </div>
      <div class="stat-card income">
        <div class="label"><Icon name="dollar" size="16" /> 年度总收入</div>
        <div class="value">¥{{ formatMoney(yearTotalIncome) }}</div>
      </div>
      <div class="stat-card balance">
        <div class="label"><Icon name="bar-chart" size="16" /> 年度结余</div>
        <div class="value" :class="{ negative: yearTotalIncome - yearTotalExpense < 0 }">
          ¥{{ formatMoney(yearTotalIncome - yearTotalExpense) }}
        </div>
      </div>
    </div>

    <!-- 月度收支柱状图 -->
    <div class="chart-wrapper" style="margin-bottom: 16px;">
      <div class="chart-title"><Icon name="bar-chart" /> 月度收支对比</div>
      <div ref="yearChartRef" style="height: 320px;"></div>
    </div>

    <!-- 月度明细表格 -->
    <div class="chart-wrapper">
      <div class="chart-title"><Icon name="list" /> 月度明细</div>
      <div class="monthly-table">
        <div class="table-header">
          <span class="col-month">月份</span>
          <span class="col-amount">收入</span>
          <span class="col-amount">支出</span>
          <span class="col-amount">结余</span>
        </div>
        <div
          v-for="m in yearlyData.monthly"
          :key="m.month"
          class="table-row"
          :class="{ 'current-month': m.month === currentMonth && selectedYear === currentYear }"
        >
          <span class="col-month">{{ m.month }}月</span>
          <span class="col-amount income-text">¥{{ formatMoney(m.income) }}</span>
          <span class="col-amount expense-text">¥{{ formatMoney(m.expense) }}</span>
          <span class="col-amount" :class="m.balance >= 0 ? 'balance-text' : 'expense-text'">
            ¥{{ formatMoney(m.balance) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getYearlyStats } from '../api'
import Icon from '../components/Icon.vue'

const loading = ref(true)
const today = new Date()
const selectedYear = ref(today.getFullYear())
const currentYear = today.getFullYear()
const currentMonth = today.getMonth() + 1
const yearChartRef = ref(null)
let chartInstance = null

const yearlyData = ref({ year: today.getFullYear(), monthly: [] })

const selectedYearDate = ref(String(today.getFullYear()))

function handleYearChange(val) {
  if (val) {
    selectedYear.value = parseInt(val, 10)
    fetchData()
  }
}

const yearTotalExpense = computed(() =>
  yearlyData.value.monthly.reduce((sum, m) => sum + m.expense, 0)
)
const yearTotalIncome = computed(() =>
  yearlyData.value.monthly.reduce((sum, m) => sum + m.income, 0)
)

function formatMoney(n) {
  return Number(n || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function renderChart() {
  if (!yearChartRef.value) return
  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(yearChartRef.value)

  const months = yearlyData.value.monthly.map(m => m.month + '月')
  const incomeData = yearlyData.value.monthly.map(m => m.income)
  const expenseData = yearlyData.value.monthly.map(m => m.expense)

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(0, 0, 0, 0.05)',
      padding: [10, 14],
      textStyle: { color: '#0f172a', fontSize: 13 },
      formatter: (params) => {
        let html = `<div style="font-weight:600;margin-bottom:6px;color:#334155">${params[0].axisValue}</div>`
        params.forEach(p => {
          html += `<div style="margin-top:4px;font-family:tabular-nums;display:flex;justify-content:space-between;gap:12px;">
                     <span>${p.marker} ${p.seriesName}</span>
                     <strong style="color:${p.color.colorStops ? p.color.colorStops[1].color : p.color}">¥${Number(p.value).toLocaleString()}</strong>
                   </div>`
        })
        return html
      },
    },
    legend: {
      data: ['收入', '支出'],
      textStyle: { color: '#64748b', fontSize: 13, fontWeight: 500 },
      top: 0,
      itemWidth: 12,
      itemHeight: 12,
      icon: 'circle'
    },
    grid: { top: 40, right: 10, bottom: 20, left: 10, containLabel: true },
    xAxis: {
      type: 'category',
      data: months,
      axisLabel: { color: '#64748b', fontSize: 11, margin: 12 },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      splitNumber: 4,
      axisLabel: {
        color: '#64748b',
        fontSize: 11,
        formatter: (v) => v >= 1000 ? (v / 1000).toFixed(1) + 'k' : v,
      },
      splitLine: { 
        lineStyle: { 
          color: 'rgba(0,0,0,0.05)', 
          type: 'solid' 
        } 
      },
    },
    series: [
      {
        name: '收入',
        type: 'bar',
        data: incomeData,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#34d399' },
            { offset: 1, color: '#10b981' },
          ]),
          borderRadius: [4, 4, 4, 4],
        },
        barMaxWidth: 16,
        barGap: '20%',
        animationDuration: 1000,
        animationEasing: 'cubicOut',
      },
      {
        name: '支出',
        type: 'bar',
        data: expenseData,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#f87171' },
            { offset: 1, color: '#ef4444' },
          ]),
          borderRadius: [4, 4, 4, 4],
        },
        barMaxWidth: 16,
        animationDuration: 1000,
        animationEasing: 'cubicOut',
        animationDelay: 100,
      },
    ],
  }, true)
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getYearlyStats(selectedYear.value)
    yearlyData.value = res.data
    await nextTick()
    renderChart()
  } catch (e) {
    console.error('Failed to load yearly data:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  window.addEventListener('resize', () => chartInstance?.resize())
})
</script>

<style scoped>
.month-selector {
  display: flex; align-items: center; justify-content: center; margin-bottom: 24px;
}
:deep(.elegant-date-picker) {
  width: 140px !important;
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

/* 自定义表格 */
.monthly-table { border-radius: 12px; overflow: hidden; border: 1px solid var(--border-color); }
.table-header {
  display: flex; padding: 14px 16px;
  background: rgba(0, 0, 0, 0.02); font-size: 13px; font-weight: 600; color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
}
.table-row {
  display: flex; padding: 14px 16px;
  border-bottom: 1px solid var(--border-color);
  font-size: 14px; transition: background 0.2s;
}
.table-row:hover { background: rgba(0, 0, 0, 0.015); }
.table-row:last-child { border-bottom: none; }
.current-month {
  background: rgba(194, 163, 131, 0.1); /* 暖棕色高亮背景 */
  border-left: 3px solid var(--primary);
}
.col-month { width: 60px; font-weight: 600; color: var(--text-primary); }
.col-amount { flex: 1; text-align: right; font-weight: 500; font-variant-numeric: tabular-nums; }
.income-text { color: var(--success); }
.expense-text { color: var(--danger); }
.balance-text { color: var(--info); }
</style>
