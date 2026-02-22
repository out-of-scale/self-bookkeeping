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
    grid: { top: 20, right: 14, bottom: 20, left: 14, containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { color: '#64748b', fontSize: 11, margin: 12 },
      axisLine: { show: false },
      axisTick: { show: false },
      boundaryGap: false,
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
      type: 'line',
      data: amounts,
      smooth: 0.4,
      symbol: 'circle',
      symbolSize: 6,
      showSymbol: false, // 只有 hover 才显示点
      lineStyle: { 
        color: '#818cf8', 
        width: 3,
        shadowColor: 'rgba(194, 163, 131, 0.3)',
        shadowBlur: 10,
        shadowOffsetY: 4
      },
      itemStyle: { color: '#818cf8', borderColor: '#fff', borderWidth: 2 },
      label: {
        show: false, // 去掉到处都是的数字，保持折线唯美
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(194, 163, 131, 0.4)' },
          { offset: 1, color: 'rgba(194, 163, 131, 0.0)' },
        ]),
      },
      animationDuration: 1200,
      animationEasing: 'cubicOut',
    }],
  }, true)
}

watch(() => props.data, render, { deep: true })
onMounted(() => { render(); window.addEventListener('resize', () => chart?.resize()) })
onUnmounted(() => { chart?.dispose(); chart = null })
</script>
