/**
 * 菜谱API客户端服务
 */
import apiClient from './api'
import type {
  GenerateRecipeRequest,
  RecipeResponse,
  SaveRecipeResponse,
  RecipeHistoryResponse,
  ImageRecognitionResponse,
  Recipe,
} from '@/types'

/**
 * 菜谱API客户端类
 */
export class RecipeAPIClient {
  /**
   * 生成菜谱
   */
  async generateRecipe(params: GenerateRecipeRequest): Promise<Recipe> {
    try {
      const response = await apiClient.post<RecipeResponse>('/recipes/generate', params)
      
      // 转换响应格式（snake_case -> camelCase）
      return this.transformRecipeResponse(response.data)
    } catch (error) {
      console.error('生成菜谱失败:', error)
      throw new Error('生成菜谱失败，请稍后重试')
    }
  }

  /**
   * 上传图片识别食材
   */
  async uploadImage(file: File): Promise<string[]> {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await apiClient.post<ImageRecognitionResponse>(
        '/images/recognize',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      return response.data.ingredients
    } catch (error) {
      console.error('图片识别失败:', error)
      throw new Error('图片识别失败，请稍后重试')
    }
  }

  /**
   * 保存菜谱
   */
  async saveRecipe(recipe: Recipe): Promise<string> {
    try {
      // 转换为后端格式（camelCase -> snake_case）
      const request: any = {
        name: recipe.name,
        image: recipe.image,
        ingredients: recipe.ingredients,
        steps: recipe.steps,
        difficulty: recipe.difficulty,
        cooking_time: recipe.cookingTime,
        servings: recipe.servings,
        safety_tips: recipe.safetyTips,
      }

      const response = await apiClient.post<SaveRecipeResponse>('/recipes/save', request)
      
      if (response.data.success) {
        return response.data.id
      } else {
        throw new Error(response.data.message || '保存失败')
      }
    } catch (error) {
      console.error('保存菜谱失败:', error)
      throw new Error('保存菜谱失败，请稍后重试')
    }
  }

  /**
   * 获取历史菜谱列表
   */
  async getRecipeHistory(limit: number = 50, offset: number = 0): Promise<RecipeHistoryResponse> {
    try {
      const response = await apiClient.get<RecipeHistoryResponse>('/recipes/history', {
        params: { limit, offset },
      })

      // 转换响应格式
      return {
        recipes: response.data.recipes.map(item => ({
          id: item.id,
          name: item.name,
          image: item.image,
          difficulty: item.difficulty,
          cookingTime: (item as any).cooking_time || item.cookingTime,
          servings: item.servings,
          createdAt: (item as any).created_at || item.createdAt,
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

  /**
   * 根据ID获取菜谱详情
   */
  async getRecipeById(id: string): Promise<Recipe> {
    try {
      const response = await apiClient.get<RecipeResponse>(`/recipes/${id}`)
      
      // 转换响应格式
      return this.transformRecipeResponse(response.data)
    } catch (error) {
      console.error('获取菜谱详情失败:', error)
      throw new Error('获取菜谱详情失败，请稍后重试')
    }
  }

  /**
   * 转换菜谱响应格式（snake_case -> camelCase）
   */
  private transformRecipeResponse(data: RecipeResponse): Recipe {
    return {
      id: data.id,
      name: data.name,
      image: data.image,
      ingredients: data.ingredients,
      steps: data.steps,
      difficulty: data.difficulty,
      cookingTime: data.cooking_time,
      servings: data.servings,
      safetyTips: data.safety_tips,
      createdAt: data.created_at,
    }
  }

  /**
   * 生成菜品效果图
   */
  async generateDishImage(recipeName: string, ingredients: string[]): Promise<string> {
    try {
      // 使用POST请求，将参数放在请求体中
      const response = await apiClient.post<{ success: boolean; image_url: string; message: string }>(
        '/recipes/generate-image',
        {
          recipe_name: recipeName,
          ingredients: ingredients
        }
      )

      if (response.data.success) {
        return response.data.image_url
      } else {
        throw new Error(response.data.message || '生成图片失败')
      }
    } catch (error) {
      console.error('生成菜品图片失败:', error)
      throw new Error('生成菜品图片失败，请稍后重试')
    }
  }

  /**
   * 询问烹饪问题（AI对话）- 流式接收
   */
  async askCookingQuestion(question: string, onChunk: (chunk: string) => void): Promise<void> {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/cooking/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
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

        // 解码数据
        const chunk = decoder.decode(value, { stream: true })
        
        // 处理SSE格式的数据
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
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
            } catch (e) {
              // 忽略JSON解析错误
              console.warn('解析SSE数据失败:', e)
            }
          }
        }
      }
    } catch (error) {
      console.error('询问烹饪问题失败:', error)
      throw new Error('AI服务暂时不可用，请稍后重试')
    }
  }

  /**
   * 诊断烹饪问题
   */
  async diagnoseCookingProblem(problem: string): Promise<string> {
    try {
      const response = await apiClient.post<{ diagnosis: string }>(
        '/cooking/diagnose',
        { problem }
      )
      return response.data.diagnosis
    } catch (error) {
      console.error('诊断烹饪问题失败:', error)
      throw new Error('诊断服务暂时不可用，请稍后重试')
    }
  }

  /**
   * 根据食材搜索菜谱
   */
  async searchByIngredients(ingredients: string[]): Promise<any[]> {
    try {
      const response = await apiClient.post<{ recipes: any[] }>(
        '/search/ingredients',
        { ingredients }
      )
      return response.data.recipes
    } catch (error) {
      console.error('搜索菜谱失败:', error)
      throw new Error('搜索服务暂时不可用，请稍后重试')
    }
  }

  /**
   * 获取食材推荐
   */
  async getIngredientRecommendation(ingredients: string[]): Promise<any> {
    try {
      const response = await apiClient.post<{ recommendation: any }>(
        '/search/recommend',
        { ingredients }
      )
      return response.data.recommendation
    } catch (error) {
      console.error('获取推荐失败:', error)
      throw new Error('推荐服务暂时不可用，请稍后重试')
    }
  }

  /**
   * 解析菜谱所需食材
   */
  async parseDishIngredients(dishName: string): Promise<any> {
    try {
      const response = await apiClient.post<{ dishInfo: any }>(
        '/search/parse-dish',
        { dishName }
      )
      return response.data.dishInfo
    } catch (error) {
      console.error('解析菜谱失败:', error)
      throw new Error('解析服务暂时不可用，请稍后重试')
    }
  }
}

// 导出单例
export const recipeApi = new RecipeAPIClient()
