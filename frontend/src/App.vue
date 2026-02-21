<template>
  <div class="app-layout">
    <div class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
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
        <span class="icon">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
const navItems = [
  { path: '/', icon: '📊', label: '概况' },
  { path: '/charts', icon: '📈', label: '分析' },
  { path: '/yearly', icon: '📅', label: '年度' },
  { path: '/records', icon: '📋', label: '明细' },
]
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: var(--bg-primary);
}
</style>
