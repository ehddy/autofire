<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>💼 AutoFIRE Dashboard</h1>
      <button @click="refreshData" class="refresh-btn">🔄 새로고침</button>
    </header>

    <!-- 로딩 상태 -->
    <div v-if="accountStore.isLoading" class="loading">
      데이터를 불러오는 중...
    </div>

    <!-- 에러 상태 -->
    <div v-if="accountStore.error" class="error">
      ⚠️ {{ accountStore.error }}
    </div>

    <!-- 계좌 요약 -->
    <div v-else class="account-summary">
      <div class="summary-card">
        <h3>총 자산</h3>
        <p class="amount">{{ formatNumber(accountStore.summary.total_assets) }} 원</p>
      </div>

      <div class="summary-card">
        <h3>예수금</h3>
        <p class="amount">{{ formatNumber(accountStore.summary.cash_balance) }} 원</p>
      </div>

      <div class="summary-card">
        <h3>보유 종목 가치</h3>
        <p class="amount">{{ formatNumber(accountStore.summary.stock_value) }} 원</p>
      </div>

      <div class="summary-card" :class="{ profit: accountStore.isProfit, loss: !accountStore.isProfit }">
        <h3>손익</h3>
        <p class="amount">
          {{ formatNumber(accountStore.summary.profit_loss) }} 원
          <span class="rate">({{ accountStore.summary.profit_rate }}%)</span>
        </p>
      </div>
    </div>

    <!-- 금일 거래 현황 -->
    <div class="today-trades">
      <h2>📊 금일 거래 현황</h2>
      <div v-if="tradingStore.todayTrades.length === 0" class="empty">
        오늘 거래 내역이 없습니다.
      </div>
      <table v-else class="trades-table">
        <thead>
          <tr>
            <th>시간</th>
            <th>종목코드</th>
            <th>구분</th>
            <th>수량</th>
            <th>체결가</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trade in tradingStore.todayTrades" :key="trade.id">
            <td>{{ formatTime(trade.executed_at) }}</td>
            <td>{{ trade.stock_code }}</td>
            <td :class="trade.order_type === 'BUY' ? 'buy' : 'sell'">
              {{ trade.order_type }}
            </td>
            <td>{{ trade.executed_quantity }}</td>
            <td>{{ formatNumber(trade.executed_price) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 보유 종목 -->
    <div class="holdings">
      <h2>📈 보유 종목 ({{ accountStore.summary.holdings_count }}개)</h2>
      <div v-if="accountStore.summary.holdings.length === 0" class="empty">
        보유 종목이 없습니다.
      </div>
      <table v-else class="holdings-table">
        <thead>
          <tr>
            <th>종목코드</th>
            <th>보유수량</th>
            <th>평균매수가</th>
            <th>현재가</th>
            <th>평가손익</th>
            <th>수익률</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="holding in accountStore.summary.holdings" :key="holding.id">
            <td>{{ holding.stock_code }}</td>
            <td>{{ holding.quantity }}</td>
            <td>{{ formatNumber(holding.avg_buy_price) }}</td>
            <td>{{ formatNumber(holding.current_price) }}</td>
            <td :class="{ profit: holding.profit_loss > 0, loss: holding.profit_loss < 0 }">
              {{ formatNumber(holding.profit_loss) }}
            </td>
            <td :class="{ profit: holding.profit_rate > 0, loss: holding.profit_rate < 0 }">
              {{ holding.profit_rate }}%
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAccountStore } from '../stores/account'
import { useTradingStore } from '../stores/trading'

const accountStore = useAccountStore()
const tradingStore = useTradingStore()

// 데이터 로드
onMounted(async () => {
  await Promise.all([
    accountStore.fetchAccountSummary(),
    tradingStore.fetchTodayTrades()
  ])
})

// 새로고침
const refreshData = async () => {
  await Promise.all([
    accountStore.fetchAccountSummary(),
    tradingStore.fetchTodayTrades()
  ])
}

// 숫자 포맷팅
const formatNumber = (value) => {
  if (!value) return '0'
  return Math.round(value).toLocaleString()
}

// 시간 포맷팅
const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.dashboard-header h1 {
  margin: 0;
  font-size: 2em;
}

.refresh-btn {
  padding: 10px 20px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
}

.refresh-btn:hover {
  background: #45a049;
}

.loading,
.error,
.empty {
  padding: 40px;
  text-align: center;
  background: #f5f5f5;
  border-radius: 8px;
  margin: 20px 0;
}

.error {
  background: #ffebee;
  color: #c62828;
}

/* 계좌 요약 카드 */
.account-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.summary-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.summary-card h3 {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 0.9em;
  text-transform: uppercase;
}

.summary-card .amount {
  margin: 0;
  font-size: 1.8em;
  font-weight: bold;
}

.summary-card.profit .amount {
  color: #d32f2f;
}

.summary-card.loss .amount {
  color: #1976d2;
}

.rate {
  font-size: 0.7em;
  margin-left: 5px;
}

/* 테이블 스타일 */
.today-trades,
.holdings {
  margin-bottom: 30px;
}

.today-trades h2,
.holdings h2 {
  margin-bottom: 15px;
}

.trades-table,
.holdings-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.trades-table th,
.holdings-table th {
  background: #2196F3;
  color: white;
  padding: 12px;
  text-align: left;
  font-weight: 600;
}

.trades-table td,
.holdings-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.trades-table tbody tr:hover,
.holdings-table tbody tr:hover {
  background: #f5f5f5;
}

.buy {
  color: #d32f2f;
  font-weight: bold;
}

.sell {
  color: #1976d2;
  font-weight: bold;
}

.profit {
  color: #d32f2f;
}

.loss {
  color: #1976d2;
}
</style>
