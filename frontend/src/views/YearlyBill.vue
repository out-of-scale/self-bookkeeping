<template>
  <div class="page-container" v-loading="loading">
    <div class="page-header">
      <h2>📅 年度账单</h2>
      <p class="subtitle">{{ selectedYear }}年收支概览</p>
    </div>

    <!-- 年份选择 -->
    <div class="month-selector">
      <button class="month-btn" @click="selectedYear--; fetchData()">◀</button>
      <span class="month-label">{{ selectedYear }}年</span>
      <button class="month-btn" @click="selectedYear++; fetchData()">▶</button>
    </div>

    <!-- 年度汇总卡片 -->
    <div class="grid-3">
      <div class="stat-card expense">
        <div class="label">💸 年度总支出</div>
        <div class="value">¥{{ formatMoney(yearTotalExpense) }}</div>
      </div>
      <div class="stat-card income">
        <div class="label">💰 年度总收入</div>
        <div class="value">¥{{ formatMoney(yearTotalIncome) }}</div>
      </div>
      <div class="stat-card balance">
        <div class="label">📊 年度结余</div>
        <div class="value" :class="{ negative: yearTotalIncome - yearTotalExpense < 0 }">
          ¥{{ formatMoney(yearTotalIncome - yearTotalExpense) }}
        </div>
      </div>
    </div>

    <!-- 月度收支柱状图 -->
    <div class="chart-wrapper" style="margin-bottom: 16px;">
      <div class="chart-title">📊 月度收支对比</div>
      <div ref="yearChartRef" style="height: 320px;"></div>
    </div>

    <!-- 月度明细表格 -->
    <div class="chart-wrapper">
      <div class="chart-title">📋 月度明细</div>
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

const loading = ref(true)
const today = new Date()
const selectedYear = ref(today.getFullYear())
const currentYear = today.getFullYear()
const currentMonth = today.getMonth() + 1
const yearChartRef = ref(null)
let chartInstance = null

const yearlyData = ref({ year: today.getFullYear(), monthly: [] })

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
      backgroundColor: 'rgba(30, 41, 59, 0.95)',
      borderColor: '#334155',
      textStyle: { color: '#f1f5f9', fontSize: 13 },
      formatter: (params) => {
        let html = `<div style="font-weight:600;">${params[0].axisValue}</div>`
        params.forEach(p => {
          html += `<div style="margin-top:4px;">${p.marker} ${p.seriesName}: ¥${Number(p.value).toLocaleString()}</div>`
        })
        return html
      },
    },
    legend: {
      data: ['收入', '支出'],
      textStyle: { color: '#94a3b8', fontSize: 12 },
      top: 0,
    },
    grid: { top: 40, right: 20, bottom: 30, left: 56 },
    xAxis: {
      type: 'category',
      data: months,
      axisLabel: { color: '#64748b', fontSize: 11 },
      axisLine: { lineStyle: { color: '#334155' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#64748b',
        fontSize: 11,
        formatter: (v) => v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v,
      },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } },
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
          borderRadius: [4, 4, 0, 0],
        },
        barMaxWidth: 20,
        label: {
          show: true, position: 'top', color: '#34d399', fontSize: 10,
          formatter: (p) => p.value > 0 ? p.value.toLocaleString() : '',
        },
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
          borderRadius: [4, 4, 0, 0],
        },
        barMaxWidth: 20,
        label: {
          show: true, position: 'top', color: '#f87171', fontSize: 10,
          formatter: (p) => p.value > 0 ? p.value.toLocaleString() : '',
        },
      },
    ],
  })
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
  display: flex; align-items: center; gap: 16px; margin-bottom: 20px;
}
.month-btn {
  width: 36px; height: 36px; border-radius: 10px;
  border: 1px solid var(--border-color); background: var(--bg-card);
  color: var(--text-primary); font-size: 14px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.month-btn:hover { border-color: var(--primary); background: var(--bg-card-hover); }
.month-label { font-size: 18px; font-weight: 600; color: var(--text-primary); }
.negative { color: #f87171 !important; }

/* 自定义表格 */
.monthly-table { border-radius: 8px; overflow: hidden; }
.table-header {
  display: flex; padding: 12px 16px;
  background: var(--bg-primary); font-size: 13px; font-weight: 600; color: var(--text-secondary);
}
.table-row {
  display: flex; padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  font-size: 14px; transition: background 0.2s;
}
.table-row:hover { background: var(--bg-card-hover); }
.table-row:last-child { border-bottom: none; }
.current-month {
  background: rgba(99, 102, 241, 0.08);
  border-left: 3px solid var(--primary);
}
.col-month { width: 60px; font-weight: 500; }
.col-amount { flex: 1; text-align: right; font-weight: 500; font-variant-numeric: tabular-nums; }
.income-text { color: #34d399; }
.expense-text { color: #f87171; }
.balance-text { color: #60a5fa; }
</style>
