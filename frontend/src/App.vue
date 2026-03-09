<template>
  <div id="app">
    <header>
      <div class="header-content">
        <div class="logo">
          <h1>🔥 AutoFIRE</h1>
          <p>자동 매매 시스템 대시보드</p>
        </div>
        <nav class="main-nav">
          <router-link to="/" class="nav-link">대시보드</router-link>
          <router-link to="/trading" class="nav-link">거래 내역</router-link>
          <router-link to="/holdings" class="nav-link">보유 종목</router-link>
        </nav>
      </div>
    </header>

    <main>
      <router-view />
    </main>

    <footer>
      <p>&copy; 2026 AutoFIRE - Financial Independence, Retire Early</p>
    </footer>
  </div>
</template>

<script setup>
// Vue 3 Composition API with script setup
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f0f2f5;
  color: #333;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Header */
header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo h1 {
  font-size: 2em;
  margin-bottom: 5px;
}

.logo p {
  font-size: 0.9em;
  opacity: 0.9;
}

.main-nav {
  display: flex;
  gap: 10px;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 10px 20px;
  border-radius: 5px;
  transition: background 0.3s;
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.3);
  font-weight: 600;
}

/* Main Content */
main {
  flex: 1;
  padding: 20px;
  background: #f0f2f5;
}

/* Footer */
footer {
  background: #2c3e50;
  color: white;
  text-align: center;
  padding: 20px;
  margin-top: auto;
}

footer p {
  font-size: 0.9em;
  opacity: 0.8;
}
</style>
