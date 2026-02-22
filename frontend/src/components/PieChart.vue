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

const COLORS = [
  '#c2a383', '#d98880', '#82a88d', '#eab676',
  '#8eb1c7', '#d6bb9f', '#e09d8d', '#769b8b', '#a9a098',
]

function render() {
  if (!chartRef.value || !props.data.length) return
  if (!chart) chart = echarts.init(chartRef.value)

  const total = props.data.reduce((s, d) => s + d.amount, 0)

  chart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(30, 41, 59, 0.95)',
      borderColor: '#334155',
      textStyle: { color: '#f1f5f9', fontSize: 13 },
      formatter: (p) => `${p.marker} ${p.name}<br/>¥${p.value.toLocaleString()} (${p.percent}%)`,
    },
    legend: {
      orient: 'horizontal',
      bottom: 0,
      left: 'center',
      textStyle: { color: '#94a3b8', fontSize: 11 },
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 12,
    },
    series: [{
      type: 'pie',
      radius: ['42%', '68%'],
      center: ['50%', '46%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 6,
        borderColor: '#1e293b',
        borderWidth: 2,
      },
      label: { show: false },
      labelLine: { show: false },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold',
          formatter: '{b}\n¥{c}',
          color: '#f1f5f9',
        },
        itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.3)' },
      },
      data: props.data.map((d, i) => ({
        name: d.category,
        value: d.amount,
        itemStyle: { color: COLORS[i % COLORS.length] },
      })),
    }],
    graphic: [{
      type: 'group',
      left: 'center',
      top: '38%',
      children: [
        {
          type: 'text',
          style: {
            text: '总计',
            fill: '#94a3b8',
            fontSize: 11,
            textAlign: 'center',
          },
          left: 'center',
          top: -10,
        },
        {
          type: 'text',
          style: {
            text: `¥${total.toLocaleString()}`,
            fill: '#f1f5f9',
            fontSize: 16,
            fontWeight: 'bold',
            textAlign: 'center',
          },
          left: 'center',
          top: 6,
        },
      ],
    }],
  }, true)
}

watch(() => props.data, render, { deep: true })
onMounted(() => { render(); window.addEventListener('resize', () => chart?.resize()) })
onUnmounted(() => { chart?.dispose(); chart = null })
</script>
