/**
 * Axios API 클라이언트 설정
 */
import axios from 'axios'

// Backend API URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1'

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    // 요청 전 처리 (예: 토큰 추가)
    console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    // 응답 데이터 처리
    console.log(`[API Response] ${response.config.url}`, response.status)
    return response
  },
  (error) => {
    // 에러 처리
    if (error.response) {
      // 서버 응답이 있는 경우
      console.error('[API Response Error]', error.response.status, error.response.data)

      if (error.response.status === 404) {
        console.warn('API 엔드포인트를 찾을 수 없습니다.')
      } else if (error.response.status === 500) {
        console.error('서버 내부 오류가 발생했습니다.')
      }
    } else if (error.request) {
      // 요청이 전송되었으나 응답이 없는 경우
      console.error('[API No Response]', error.request)
    } else {
      // 요청 설정 중 오류가 발생한 경우
      console.error('[API Setup Error]', error.message)
    }

    return Promise.reject(error)
  }
)

export default api
