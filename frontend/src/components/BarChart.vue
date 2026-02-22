<template>
  <div ref="chartRef" :style="{ height: height + 'px' }"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: { type: Array, default: () => [] },
  height: { type: Number, default: 280 },
})

const chartRef = ref(null)
let chart = null

function render() {
  if (!chartRef.value || !props.data.length) return
  if (!chart) chart = echarts.init(chartRef.value)

  const dates = props.data.map(d => d.date.slice(5))
  const amounts = props.data.map(d => d.amount)
  const max = Math.max(...amounts)

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(0, 0, 0, 0.05)',
      padding: [8, 12],
      textStyle: { color: '#0f172a', fontSize: 13 },
      formatter: (params) => {
        const p = params[0]
        return `<div style="font-weight:600;margin-bottom:4px;color:#334155">${p.axisValue}</div>
                <div style="font-family:tabular-nums">支出: ¥${Number(p.value).toLocaleString()}</div>`
      },
    },
    grid: { top: 30, right: 10, bottom: 20, left: 10, containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { color: '#64748b', fontSize: 11, margin: 12 },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      splitNumber: 3,
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
    series: [{
      type: 'bar',
      data: amounts,
      barWidth: '35%',
      barMaxWidth: 30,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#d6bb9f' },
          { offset: 1, color: '#c2a383' },
        ]),
        borderRadius: [6, 6, 6, 6],
      },
      animationDuration: 1000,
      animationEasing: 'cubicOut',
      label: {
        show: false, // 移除柱子顶部的文字，使图表更干净，信息通过 Tooltip 展示
      },
    }],
  }, true)
}

watch(() => props.data, render, { deep: true })
onMounted(() => { render(); window.addEventListener('resize', () => chart?.resize()) })
onUnmounted(() => { chart?.dispose(); chart = null })
</script>
