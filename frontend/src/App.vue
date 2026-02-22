<template>
  <div class="app-layout">
    <div class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade-slide" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>

    <!-- 底部导航栏 -->
    <nav class="bottom-nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: $route.path === item.path }"
      >
        <span class="icon"><Icon :name="item.icon" size="24" /></span>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import Icon from './components/Icon.vue'

const navItems = [
  { path: '/', icon: 'bar-chart', label: '概况' },
  { path: '/charts', icon: 'trending-up', label: '分析' },
  { path: '/yearly', icon: 'calendar', label: '年度' },
  { path: '/records', icon: 'list', label: '明细' },
]
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: var(--bg-primary);
}
</style>
