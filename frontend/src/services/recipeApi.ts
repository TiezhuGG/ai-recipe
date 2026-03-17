/**
 * Recipe API client.
 */
import apiClient from './api'
import { buildApiUrl, resolveAssetUrl } from './apiConfig'
import type {
  GenerateRecipeRequest,
  RecipeResponse,
  SaveRecipeResponse,
  SessionInitResponse,
  RecipeHistoryResponse,
  ImageRecognitionResponse,
  Recipe,
} from '@/types'

export class RecipeAPIClient {
  private sessionReadyPromise: Promise<void> | null = null

  async ensureSession(force = false): Promise<void> {
    if (force || !this.sessionReadyPromise) {
      this.sessionReadyPromise = apiClient
        .get<SessionInitResponse>('/session/init')
        .then((response) => {
          if (!response.data.success) {
            throw new Error(response.data.message || '初始化会话失败')
          }
        })
        .catch((error) => {
          this.sessionReadyPromise = null
          console.error('初始化会话失败:', error)
          throw new Error('初始化会话失败，请刷新页面后重试')
        })
    }

    return this.sessionReadyPromise
  }

  private async withSession<T>(request: () => Promise<T>): Promise<T> {
    await this.ensureSession()

    try {
      return await request()
    } catch (error: any) {
      if (error?.response?.status === 403) {
        this.sessionReadyPromise = null
        await this.ensureSession(true)
        return request()
      }

      throw error
    }
  }

  async generateRecipe(params: GenerateRecipeRequest): Promise<Recipe> {
    try {
      const response = await apiClient.post<RecipeResponse>('/recipes/generate', params)
      return this.transformRecipeResponse(response.data)
    } catch (error) {
      console.error('生成菜谱失败:', error)
      throw new Error('生成菜谱失败，请稍后重试')
    }
  }

  async uploadImage(file: File): Promise<string[]> {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await apiClient.post<ImageRecognitionResponse>('/images/recognize', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      return response.data.ingredients
    } catch (error) {
      console.error('图片识别失败:', error)
      throw new Error('图片识别失败，请稍后重试')
    }
  }

  async saveRecipe(recipe: Recipe): Promise<string> {
    try {
      const request = {
        name: recipe.name,
        image: recipe.image,
        ingredients: recipe.ingredients,
        steps: recipe.steps,
        difficulty: recipe.difficulty,
        cooking_time: recipe.cookingTime,
        servings: recipe.servings,
        safety_tips: recipe.safetyTips,
      }

      const response = await this.withSession(() =>
        apiClient.post<SaveRecipeResponse>('/recipes/save', request)
      )

      if (!response.data.success) {
        throw new Error(response.data.message || '保存失败')
      }

      return response.data.id
    } catch (error) {
      console.error('保存菜谱失败:', error)
      throw new Error('保存菜谱失败，请稍后重试')
    }
  }

  async getRecipeHistory(limit = 50, offset = 0): Promise<RecipeHistoryResponse> {
    try {
      const response = await this.withSession(() =>
        apiClient.get<RecipeHistoryResponse>('/recipes/history', {
          params: { limit, offset },
        })
      )

      return {
        recipes: response.data.recipes.map((item: any) => ({
          id: item.id,
          name: item.name,
          image: resolveAssetUrl(item.image),
          difficulty: item.difficulty,
          cookingTime: item.cooking_time || item.cookingTime,
          servings: item.servings,
          createdAt: item.created_at || item.createdAt,
        })),
        total: response.data.total,
        limit: response.data.limit,
        offset: response.data.offset,
      }
    } catch (error) {
      console.error('获取历史记录失败:', error)
      throw new Error('获取历史记录失败，请稍后重试')
    }
  }

  async getRecipeById(id: string): Promise<Recipe> {
    try {
      const response = await this.withSession(() => apiClient.get<RecipeResponse>(`/recipes/${id}`))
      return this.transformRecipeResponse(response.data)
    } catch (error) {
      console.error('获取菜谱详情失败:', error)
      throw new Error('获取菜谱详情失败，请稍后重试')
    }
  }

  private transformRecipeResponse(data: RecipeResponse): Recipe {
    return {
      id: data.id,
      name: data.name,
      image: resolveAssetUrl(data.image),
      ingredients: data.ingredients,
      steps: data.steps,
      difficulty: data.difficulty,
      cookingTime: data.cooking_time,
      servings: data.servings,
      safetyTips: data.safety_tips,
      createdAt: data.created_at,
    }
  }

  async generateDishImage(recipeName: string, ingredients: string[]): Promise<string> {
    try {
      const response = await apiClient.post<{ success: boolean; image_url: string; message: string }>(
        '/recipes/generate-image',
        {
          recipe_name: recipeName,
          ingredients,
        }
      )

      if (!response.data.success) {
        throw new Error(response.data.message || '生成图片失败')
      }

      return response.data.image_url
    } catch (error) {
      console.error('生成菜品图片失败:', error)
      throw new Error('生成菜品图片失败，请稍后重试')
    }
  }

  async askCookingQuestion(question: string, onChunk: (chunk: string) => void): Promise<void> {
    try {
      const response = await fetch(buildApiUrl('/cooking/ask'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('无法读取响应流')
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) {
          break
        }

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (!line.startsWith('data: ')) {
            continue
          }

          const data = line.slice(6)

          try {
            const parsed = JSON.parse(data)

            if (parsed.error) {
              throw new Error(parsed.error)
            }

            if (parsed.done) {
              return
            }

            if (parsed.content) {
              onChunk(parsed.content)
            }
          } catch (parseError) {
            console.warn('解析 SSE 数据失败:', parseError)
          }
        }
      }
    } catch (error) {
      console.error('烹饪问答失败:', error)
      throw new Error('AI 服务暂时不可用，请稍后重试')
    }
  }

  async diagnoseCookingProblem(problem: string): Promise<string> {
    try {
      const response = await apiClient.post<{ diagnosis: string }>('/cooking/diagnose', { problem })
      return response.data.diagnosis
    } catch (error) {
      console.error('诊断烹饪问题失败:', error)
      throw new Error('诊断服务暂时不可用，请稍后重试')
    }
  }

  async searchByIngredients(ingredients: string[]): Promise<any[]> {
    try {
      const response = await apiClient.post<{ recipes: any[] }>('/search/ingredients', { ingredients })
      return response.data.recipes
    } catch (error) {
      console.error('搜索菜谱失败:', error)
      throw new Error('搜索服务暂时不可用，请稍后重试')
    }
  }

  async getIngredientRecommendation(ingredients: string[]): Promise<any> {
    try {
      const response = await apiClient.post<{ recommendation: any }>('/search/recommend', { ingredients })
      return response.data.recommendation
    } catch (error) {
      console.error('获取推荐失败:', error)
      throw new Error('推荐服务暂时不可用，请稍后重试')
    }
  }

  async parseDishIngredients(dishName: string): Promise<any> {
    try {
      const response = await apiClient.post<{ dishInfo: any }>('/search/parse-dish', { dishName })
      return response.data.dishInfo
    } catch (error) {
      console.error('解析菜谱失败:', error)
      throw new Error('解析服务暂时不可用，请稍后重试')
    }
  }
}

export const recipeApi = new RecipeAPIClient()
