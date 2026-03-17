/**
 * 菜谱相关类型定义
 */

// 食材
export interface Ingredient {
  name: string
  amount: string
  unit: string
}

// 菜谱食材（分主料和配料）
export interface RecipeIngredients {
  main: Ingredient[]
  secondary: Ingredient[]
}

// 烹饪步骤
export interface Step {
  order: number
  description: string
  image?: string
}

// 难度级别
export type Difficulty = 'easy' | 'medium' | 'hard'

// 完整菜谱
export interface Recipe {
  id?: string
  name: string
  image?: string
  ingredients: RecipeIngredients
  steps: Step[]
  difficulty: Difficulty
  cookingTime: number // 分钟
  servings: number
  safetyTips?: string[]
  createdAt?: string
}

// 菜谱列表项（简化版）
export interface RecipeListItem {
  id: string
  name: string
  image?: string
  difficulty: Difficulty
  cookingTime: number
  servings: number
  createdAt?: string
}

// 生成菜谱参数
export interface GenerateParams {
  ingredients: string[]
  flavorTags: string[]
  cuisineTypes: string[]
  specialGroups: string[]
  recognizedIngredients?: string[]
}

// 生成菜谱请求
export interface GenerateRecipeRequest {
  ingredients: string[]
  flavor_tags: string[]
  cuisine_types: string[]
  special_groups: string[]
  recognized_ingredients?: string[]
}

// 菜谱响应
export interface RecipeResponse {
  id?: string
  name: string
  image?: string
  ingredients: RecipeIngredients
  steps: Step[]
  difficulty: Difficulty
  cooking_time: number
  servings: number
  safety_tips?: string[]
  created_at?: string
}

// 保存菜谱请求
export interface SaveRecipeRequest {
  name: string
  image?: string
  ingredients: RecipeIngredients
  steps: Step[]
  difficulty: Difficulty
  cooking_time: number
  servings: number
  safety_tips?: string[]
}

// 保存菜谱响应
export interface SaveRecipeResponse {
  id: string
  success: boolean
  message: string
}

// 历史菜谱响应
export interface SessionInitResponse {
  success: boolean
  message: string
}

export interface RecipeHistoryResponse {
  recipes: RecipeListItem[]
  total: number
  limit: number
  offset: number
}

// 图片识别响应
export interface ImageRecognitionResponse {
  ingredients: string[]
  confidence: number
  message: string
}

// API错误响应
export interface ErrorResponse {
  error: string
  detail?: string
}
