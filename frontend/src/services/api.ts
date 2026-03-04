import axios, { AxiosInstance, AxiosError } from 'axios'

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 120000,
  withCredentials: true, // 发送Cookie
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error: AxiosError) => {
    // 统一错误处理
    if (error.response) {
      const status = error.response.status
      const data: any = error.response.data

      switch (status) {
        case 400:
          console.error('请求参数错误:', data.detail || data.error)
          break
        case 403:
          console.error('无权访问:', data.detail || data.error)
          break
        case 404:
          console.error('资源不存在:', data.detail || data.error)
          break
        case 500:
          console.error('服务器错误:', data.detail || data.error)
          break
        default:
          console.error('请求失败:', data.detail || data.error)
      }
    } else if (error.request) {
      console.error('网络错误，请检查网络连接')
    } else {
      console.error('请求配置错误:', error.message)
    }

    return Promise.reject(error)
  }
)

export default apiClient
