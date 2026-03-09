<template>
  <div class="holdings">
    <header>
      <h1>📊 보유 종목</h1>
      <button @click="fetchData" class="refresh-btn">🔄 새로고침</button>
    </header>

    <div v-if="accountStore.isLoading" class="loading">
      데이터를 불러오는 중...
    </div>
    <div v-else-if="accountStore.holdings.length === 0" class="empty">
      보유 종목이 없습니다.
    </div>
    <div v-else>
      <!-- 총 평가 금액 -->
      <div class="total-value">
        <h2>총 평가금액</h2>
        <p class="amount">{{ formatNumber(totalValue) }} 원</p>
        <p class="profit-loss" :class="{ profit: totalProfitLoss > 0, loss: totalProfitLoss < 0 }">
          {{ totalProfitLoss > 0 ? '+' : '' }}{{ formatNumber(totalProfitLoss) }} 원
          ({{ totalProfitRate.toFixed(2) }}%)
        </p>
      </div>

      <!-- 보유 종목 테이블 -->
      <table class="holdings-table">
        <thead>
          <tr>
            <th>종목코드</th>
            <th>보유수량</th>
            <th>평균매수가</th>
            <th>현재가</th>
            <th>평가금액</th>
            <th>평가손익</th>
            <th>수익률</th>
            <th>비중</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="holding in accountStore.holdings" :key="holding.id">
            <td class="stock-code">{{ holding.stock_code }}</td>
            <td>{{ holding.quantity }}</td>
            <td>{{ formatNumber(holding.avg_buy_price) }}</td>
            <td>{{ formatNumber(holding.current_price) }}</td>
            <td>{{ formatNumber(holding.quantity * holding.current_price) }}</td>
            <td :class="{ profit: holding.profit_loss > 0, loss: holding.profit_loss < 0 }">
              {{ holding.profit_loss > 0 ? '+' : '' }}{{ formatNumber(holding.profit_loss) }}
            </td>
            <td :class="{ profit: holding.profit_rate > 0, loss: holding.profit_rate < 0 }">
              {{ holding.profit_rate > 0 ? '+' : '' }}{{ holding.profit_rate }}%
            </td>
            <td>{{ calculateWeight(holding) }}%</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAccountStore } from '../stores/account'

const accountStore = useAccountStore()

onMounted(async () => {
  await accountStore.fetchHoldings()
})

const fetchData = async () => {
  await accountStore.fetchHoldings()
}

// 총 평가금액
const totalValue = computed(() => {
  return accountStore.holdings.reduce((sum, h) => {
    return sum + (h.quantity * h.current_price)
  }, 0)
})

// 총 평가손익
const totalProfitLoss = computed(() => {
  return accountStore.holdings.reduce((sum, h) => {
    return sum + parseFloat(h.profit_loss || 0)
  }, 0)
})

// 총 수익률
const totalProfitRate = computed(() => {
  const totalInvested = totalValue.value - totalProfitLoss.value
  if (totalInvested === 0) return 0
  return (totalProfitLoss.value / totalInvested) * 100
})

// 비중 계산
const calculateWeight = (holding) => {
  const holdingValue = holding.quantity * holding.current_price
  if (totalValue.value === 0) return 0
  return ((holdingValue / totalValue.value) * 100).toFixed(2)
}

const formatNumber = (value) => {
  if (!value) return '0'
  return Math.round(value).toLocaleString()
}
</script>

<style scoped>
.holdings {
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

.total-value {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  text-align: center;
}

.total-value h2 {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 1.2em;
}

.total-value .amount {
  margin: 0;
  font-size: 2.5em;
  font-weight: bold;
}

.total-value .profit-loss {
  margin: 10px 0 0 0;
  font-size: 1.5em;
  font-weight: bold;
}

.holdings-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.holdings-table th {
  background: #2196F3;
  color: white;
  padding: 15px;
  text-align: left;
  font-weight: 600;
}

.holdings-table td {
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.holdings-table tbody tr:hover {
  background: #f5f5f5;
}

.stock-code {
  font-weight: bold;
  font-size: 1.1em;
}

.profit {
  color: #d32f2f;
  font-weight: bold;
}

.loss {
  color: #1976d2;
  font-weight: bold;
}

.loading,
.empty {
  padding: 40px;
  text-align: center;
  background: #f5f5f5;
  border-radius: 8px;
}
</style>
