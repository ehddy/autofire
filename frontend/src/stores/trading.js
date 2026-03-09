/**
 * 거래 내역 Pinia Store
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useTradingStore = defineStore('trading', () => {
  // State
  const trades = ref([])
  const todayTrades = ref([])
  const stats = ref({
    total_trades: 0,
    buy_count: 0,
    sell_count: 0,
    total_profit_loss: 0,
    win_rate: 0,
    win_count: 0
  })
  const isLoading = ref(false)
  const error = ref(null)

  // Actions
  async function fetchTradeHistory(params = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get('/trading/history', { params })
      trades.value = response.data
    } catch (err) {
      error.value = err.message
      console.error('거래 내역 조회 실패:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTodayTrades() {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get('/trading/history/today')
      todayTrades.value = response.data
    } catch (err) {
      error.value = err.message
      console.error('금일 거래 내역 조회 실패:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTradingStats(days = 30) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get('/trading/stats/summary', {
        params: { days }
      })
      stats.value = response.data
    } catch (err) {
      error.value = err.message
      console.error('거래 통계 조회 실패:', err)
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    trades,
    todayTrades,
    stats,
    isLoading,
    error,
    // Actions
    fetchTradeHistory,
    fetchTodayTrades,
    fetchTradingStats
  }
})
