import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Charts from '../views/Charts.vue'
import YearlyBill from '../views/YearlyBill.vue'
import Records from '../views/Records.vue'

const routes = [
    { path: '/', name: 'Dashboard', component: Dashboard, meta: { title: '本月概况' } },
    { path: '/charts', name: 'Charts', component: Charts, meta: { title: '图表分析' } },
    { path: '/yearly', name: 'YearlyBill', component: YearlyBill, meta: { title: '年度账单' } },
    { path: '/records', name: 'Records', component: Records, meta: { title: '账单明细' } },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
