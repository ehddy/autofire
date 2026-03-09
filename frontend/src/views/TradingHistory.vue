<template>
  <div class="trading-history">
    <header>
      <h1>📜 거래 내역</h1>
      <button @click="fetchData" class="refresh-btn">🔄 새로고침</button>
    </header>

    <!-- 통계 요약 -->
    <div class="stats-summary">
      <div class="stat-card">
        <h3>총 거래</h3>
        <p class="value">{{ tradingStore.stats.total_trades }}회</p>
      </div>
      <div class="stat-card">
        <h3>매수</h3>
        <p class="value buy">{{ tradingStore.stats.buy_count }}회</p>
      </div>
      <div class="stat-card">
        <h3>매도</h3>
        <p class="value sell">{{ tradingStore.stats.sell_count }}회</p>
      </div>
      <div class="stat-card">
        <h3>총 손익</h3>
        <p class="value" :class="{ profit: tradingStore.stats.total_profit_loss > 0, loss: tradingStore.stats.total_profit_loss < 0 }">
          {{ formatNumber(tradingStore.stats.total_profit_loss) }} 원
        </p>
      </div>
      <div class="stat-card">
        <h3>승률</h3>
        <p class="value">{{ tradingStore.stats.win_rate }}%</p>
      </div>
    </div>

    <!-- 필터 -->
    <div class="filters">
      <select v-model="orderTypeFilter" @change="applyFilter">
        <option value="">전체</option>
        <option value="BUY">매수</option>
        <option value="SELL">매도</option>
      </select>
      <input
        v-model="stockCodeFilter"
        @input="applyFilter"
        type="text"
        placeholder="종목코드 검색"
      />
    </div>

    <!-- 거래 내역 테이블 -->
    <div v-if="tradingStore.isLoading" class="loading">
      데이터를 불러오는 중...
    </div>
    <div v-else-if="tradingStore.trades.length === 0" class="empty">
      거래 내역이 없습니다.
    </div>
    <table v-else class="trades-table">
      <thead>
        <tr>
          <th>체결 시각</th>
          <th>종목코드</th>
          <th>구분</th>
          <th>주문수량</th>
          <th>체결수량</th>
          <th>체결가</th>
          <th>전략</th>
          <th>손익</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="trade in tradingStore.trades" :key="trade.id">
          <td>{{ formatDateTime(trade.executed_at) }}</td>
          <td>{{ trade.stock_code }}</td>
          <td :class="trade.order_type === 'BUY' ? 'buy' : 'sell'">
            {{ trade.order_type }}
          </td>
          <td>{{ trade.order_quantity }}</td>
          <td>{{ trade.executed_quantity }}</td>
          <td>{{ formatNumber(trade.executed_price) }}</td>
          <td>{{ trade.strategy_name || '-' }}</td>
          <td :class="{ profit: trade.profit_loss > 0, loss: trade.profit_loss < 0 }">
            {{ trade.profit_loss ? formatNumber(trade.profit_loss) : '-' }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTradingStore } from '../stores/trading'

const tradingStore = useTradingStore()

const orderTypeFilter = ref('')
const stockCodeFilter = ref('')

onMounted(async () => {
  await Promise.all([
    tradingStore.fetchTradeHistory(),
    tradingStore.fetchTradingStats(30)
  ])
})

const applyFilter = async () => {
  const params = {}
  if (orderTypeFilter.value) params.order_type = orderTypeFilter.value
  if (stockCodeFilter.value) params.stock_code = stockCodeFilter.value

  await tradingStore.fetchTradeHistory(params)
}

const fetchData = async () => {
  await Promise.all([
    tradingStore.fetchTradeHistory(),
    tradingStore.fetchTradingStats(30)
  ])
}

const formatNumber = (value) => {
  if (!value) return '0'
  return Math.round(value).toLocaleString()
}

const formatDateTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('ko-KR')
}
</script>

<style scoped>
.trading-history {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.refresh-btn {
  padding: 10px 20px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-card h3 {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 0.85em;
}

.stat-card .value {
  margin: 0;
  font-size: 1.5em;
  font-weight: bold;
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.filters select,
.filters input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1em;
}

.trades-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.trades-table th {
  background: #2196F3;
  color: white;
  padding: 12px;
  text-align: left;
}

.trades-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.trades-table tbody tr:hover {
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

.loading,
.empty {
  padding: 40px;
  text-align: center;
  background: #f5f5f5;
  border-radius: 8px;
}
</style>
