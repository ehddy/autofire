<template>
  <div id="app">
    <header>
      <h1>AutoFIRE</h1>
      <p>자동 매매 시스템 대시보드</p>
    </header>

    <main>
      <div class="dashboard">
        <h2>계좌 정보</h2>
        <div class="account-info">
          <p>총 자산: {{ accountInfo.total_assets?.toLocaleString() }}원</p>
          <p>예수금: {{ accountInfo.cash_balance?.toLocaleString() }}원</p>
          <p>주식 평가액: {{ accountInfo.stock_value?.toLocaleString() }}원</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'App',
  setup() {
    const accountInfo = ref({
      total_assets: 0,
      cash_balance: 0,
      stock_value: 0
    })

    const fetchAccountInfo = async () => {
      try {
        const response = await fetch('/api/v1/account/summary')
        const data = await response.json()
        accountInfo.value = data
      } catch (error) {
        console.error('Failed to fetch account info:', error)
      }
    }

    onMounted(() => {
      fetchAccountInfo()
    })

    return {
      accountInfo
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f5f5;
}

#app {
  min-height: 100vh;
}

header {
  background: #2c3e50;
  color: white;
  padding: 2rem;
  text-align: center;
}

header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

main {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.dashboard {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dashboard h2 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.account-info p {
  padding: 0.5rem 0;
  font-size: 1.1rem;
}
</style>
