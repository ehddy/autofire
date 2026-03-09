/**
 * 계좌 정보 Pinia Store
 * 실시간 데이터는 KIS API에서, 히스토리는 DB에서 조회
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAccountStore = defineStore('account', () => {
  // State
  const summary = ref({
    total_assets: 0,
    cash_balance: 0,
    stock_value: 0,
    profit_loss: 0,
    profit_rate: 0,
    holdings_count: 0,
    holdings: []
  })

  const holdings = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const totalAssets = computed(() => summary.value.total_assets)
  const profitRate = computed(() => summary.value.profit_rate)
  const isProfit = computed(() => summary.value.profit_loss > 0)

  // Actions - 실시간 데이터 (KIS API)
  async function fetchAccountSummary() {
    isLoading.value = true
    error.value = null

    try {
      // 실시간 데이터 조회 (KIS API)
      const response = await api.get('/live/account/summary')
      summary.value = response.data
      console.log('✅ 실시간 계좌 데이터 로드')
    } catch (err) {
      error.value = err.message
      console.error('계좌 요약 조회 실패:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchHoldings() {
    isLoading.value = true
    error.value = null

    try {
      // 실시간 보유 종목 조회 (KIS API)
      const response = await api.get('/live/account/holdings')
      holdings.value = response.data
      console.log('✅ 실시간 보유 종목 로드')
    } catch (err) {
      error.value = err.message
      console.error('보유 종목 조회 실패:', err)
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    summary,
    holdings,
    isLoading,
    error,
    // Getters
    totalAssets,
    profitRate,
    isProfit,
    // Actions
    fetchAccountSummary,
    fetchHoldings
  }
})
