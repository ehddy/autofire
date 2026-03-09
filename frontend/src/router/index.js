/**
 * Vue Router 설정
 */
import { createRouter, createWebHistory } from 'vue-router'

// 뷰 컴포넌트 import
import Dashboard from '../views/Dashboard.vue'
import TradingHistory from '../views/TradingHistory.vue'
import Holdings from '../views/Holdings.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: 'Dashboard - AutoFIRE' }
  },
  {
    path: '/trading',
    name: 'TradingHistory',
    component: TradingHistory,
    meta: { title: 'Trading History - AutoFIRE' }
  },
  {
    path: '/holdings',
    name: 'Holdings',
    component: Holdings,
    meta: { title: 'Holdings - AutoFIRE' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 페이지 제목 변경
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'AutoFIRE'
  next()
})

export default router
