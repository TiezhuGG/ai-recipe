/**
 * API调用状态管理组合式函数
 */
import { ref, Ref } from 'vue'

export interface UseApiReturn<T> {
  data: Ref<T | null>
  loading: Ref<boolean>
  error: Ref<string | null>
  execute: (...args: any[]) => Promise<T | null>
  reset: () => void
}

/**
 * 用于管理API调用的加载状态和错误处理
 */
export function useApi<T>(
  apiFunction: (...args: any[]) => Promise<T>
): UseApiReturn<T> {
  const data = ref<T | null>(null) as Ref<T | null>
  const loading = ref(false)
  const error = ref<string | null>(null)

  const execute = async (...args: any[]): Promise<T | null> => {
    loading.value = true
    error.value = null
    data.value = null

    try {
      const result = await apiFunction(...args)
      data.value = result
      return result
    } catch (err: any) {
      error.value = err.message || '请求失败'
      console.error('API调用失败:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  const reset = () => {
    data.value = null
    loading.value = false
    error.value = null
  }

  return {
    data,
    loading,
    error,
    execute,
    reset,
  }
}
