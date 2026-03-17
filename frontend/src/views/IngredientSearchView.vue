<template>
  <div class="ingredient-search-view min-h-screen bg-gradient-to-br from-green-900 via-teal-900 to-cyan-900 py-8">
    <div class="container mx-auto px-4 max-w-7xl">
      <!-- 头部 -->
      <div class="mb-8">
        <NavigationBar
          icon="🔍"
          title="随料大搜"
          subtitle="智能食材搜索，发现无限可能"
          current-route="search"
        />
      </div>

      <!-- 搜索区域 -->
      <div class="card-dark p-8 mb-6">
        <!-- 搜索输入 -->
        <div class="mb-6 space-y-3 sm:flex sm:items-stretch sm:gap-3 sm:space-y-0">
          <input
            v-model="searchQuery"
            @keyup.enter="handleSearch"
            @input="handleInputChange"
            type="text"
            placeholder="🔍 输入食材名称，如：番茄、鸡蛋、牛肉..."
            class="w-full px-6 py-4 bg-gray-700 border-2 border-gray-600 rounded-lg text-gray-200 placeholder-gray-500 focus:border-primary-500 focus:outline-none text-lg sm:flex-1"
          />
          <button
            type="button"
            @click="handleSearch"
            :disabled="!searchQuery.trim()"
            class="w-full rounded-lg bg-primary-500 px-8 py-4 text-lg font-medium text-gray-900 transition hover:bg-primary-400 disabled:bg-gray-600 disabled:text-gray-400 sm:w-auto"
          >
            搜索
          </button>
        </div>

        <!-- 搜索建议 -->
        <div v-if="suggestions.length > 0 && showSuggestions" class="mb-4">
          <div class="bg-gray-700 rounded-lg p-4 border border-gray-600">
            <div class="text-sm text-gray-400 mb-2">搜索建议：</div>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="suggestion in suggestions"
                :key="suggestion"
                @click="selectSuggestion(suggestion)"
                class="px-3 py-1 bg-gray-600 text-gray-300 rounded-full text-sm hover:bg-primary-500 hover:text-white transition"
              >
                {{ suggestion }}
              </button>
            </div>
          </div>
        </div>

        <!-- 已选食材 -->
        <div v-if="selectedIngredients.length > 0" class="mb-4">
          <div class="flex items-center gap-2 mb-2">
            <span class="text-sm text-gray-400">已选食材：</span>
            <button
              @click="clearIngredients"
              class="text-xs text-gray-500 hover:text-primary-400 transition"
            >
              清空
            </button>
          </div>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="(ingredient, index) in selectedIngredients"
              :key="index"
              class="px-4 py-2 bg-primary-500 text-gray-900 rounded-full flex items-center gap-2 font-medium"
            >
              <span>{{ ingredient }}</span>
              <button
                @click="removeIngredient(index)"
                class="hover:text-red-400 transition font-bold"
              >
                ×
              </button>
            </div>
          </div>
        </div>

        <!-- 快捷操作 -->
        <div class="flex gap-3">
          <button
            @click="getAIRecommendation"
            :disabled="selectedIngredients.length === 0 || isLoadingRecommendation"
            class="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition font-medium disabled:from-gray-600 disabled:to-gray-600"
          >
            {{ isLoadingRecommendation ? '🤖 AI思考中...' : '🤖 AI推荐组合' }}
          </button>
          <button
            @click="generateRecipeDirectly"
            :disabled="selectedIngredients.length === 0"
            class="px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg hover:from-orange-600 hover:to-red-600 transition font-medium disabled:from-gray-600 disabled:to-gray-600"
          >
            ⚡ 一键生成菜谱
          </button>
        </div>
      </div>

      <!-- AI推荐区域 -->
      <div v-if="aiRecommendation" class="card-dark p-6 mb-6">
        <h3 class="text-xl font-bold text-primary-400 mb-4">🤖 AI推荐</h3>
        <div class="space-y-4">
          <!-- 推荐食材 -->
          <div v-if="aiRecommendation.suggestedIngredients">
            <div class="text-sm text-gray-400 mb-2">建议添加的食材：</div>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="ingredient in aiRecommendation.suggestedIngredients"
                :key="ingredient"
                @click="addIngredient(ingredient)"
                class="px-3 py-1 bg-gray-700 text-gray-300 rounded-full text-sm hover:bg-primary-500 hover:text-white transition border border-gray-600"
              >
                + {{ ingredient }}
              </button>
            </div>
          </div>

          <!-- 推荐菜谱 -->
          <div v-if="aiRecommendation.recommendedDishes">
            <div class="text-sm text-gray-400 mb-2">推荐菜谱：</div>
            <div class="grid md:grid-cols-3 gap-3">
              <div
                v-for="dish in aiRecommendation.recommendedDishes"
                :key="dish"
                class="p-3 bg-gray-700 rounded-lg hover:bg-primary-500/20 hover:border-primary-500 cursor-pointer transition border border-gray-600"
                @click="handleDishClick(dish)"
              >
                <div class="text-primary-300 font-medium">{{ dish }}</div>
                <div class="text-xs text-gray-500 mt-1">点击直接生成</div>
              </div>
            </div>
          </div>

          <!-- 营养建议 -->
          <div v-if="aiRecommendation.nutritionTips" class="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <div class="text-sm text-blue-300 mb-1">💡 营养建议</div>
            <div class="text-sm text-gray-300">{{ aiRecommendation.nutritionTips }}</div>
          </div>
        </div>
      </div>

      <!-- 搜索结果 -->
      <div v-if="searchResults.length > 0" class="card-dark p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-primary-400">
            搜索结果 ({{ searchResults.length }}个菜谱)
          </h3>
          <div class="flex gap-2">
            <select
              v-model="sortBy"
              class="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-gray-300 text-sm"
            >
              <option value="relevance">相关度</option>
              <option value="difficulty">难度</option>
              <option value="time">时间</option>
            </select>
          </div>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="recipe in sortedResults"
            :key="recipe.id"
            @click="viewRecipe(recipe)"
            class="p-4 bg-gray-700 rounded-lg hover:bg-gray-600 cursor-pointer transition border border-gray-600 hover:border-primary-500"
          >
            <div class="flex items-start justify-between mb-2">
              <h4 class="font-bold text-primary-300 text-lg">{{ recipe.name }}</h4>
              <span class="text-xs px-2 py-1 bg-primary-500/20 text-primary-400 rounded">
                {{ recipe.difficulty === 'easy' ? '简单' : recipe.difficulty === 'medium' ? '中等' : '困难' }}
              </span>
            </div>
            <div class="text-sm text-gray-400 mb-3">
              ⏱️ {{ recipe.cooking_time }}分钟 | 👥 {{ recipe.servings }}人份
            </div>
            <div class="flex flex-wrap gap-1 mb-3">
              <span
                v-for="ingredient in recipe.matchedIngredients"
                :key="ingredient"
                class="text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded"
              >
                {{ ingredient }}
              </span>
            </div>
            <div class="text-xs text-gray-500">
              匹配度: {{ recipe.matchScore }}%
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="hasSearched && !isSearching" class="card-dark p-12 text-center">
        <div class="text-6xl mb-4">🔍</div>
        <div class="text-xl text-gray-400 mb-2">未找到相关菜谱</div>
        <div class="text-sm text-gray-500">试试其他食材或使用AI推荐功能</div>
      </div>

      <!-- 加载状态 -->
      <div v-if="isSearching" class="card-dark p-12 text-center">
        <div class="text-6xl mb-4 animate-bounce">🔍</div>
        <div class="text-xl text-gray-400">搜索中...</div>
      </div>

      <!-- 热门搜索 -->
      <div v-if="!hasSearched" class="card-dark p-6 mt-6">
        <h3 class="text-lg font-bold text-primary-400 mb-4">🔥 热门搜索</h3>
        <div class="grid md:grid-cols-4 gap-3">
          <button
            v-for="popular in popularSearches"
            :key="popular"
            @click="searchQuery = popular; handleSearch()"
            class="p-3 bg-gray-700 text-gray-300 rounded-lg hover:bg-primary-500 hover:text-white transition text-sm"
          >
            {{ popular }}
          </button>
        </div>
      </div>
    </div>

    <!-- 确认生成弹窗 -->
    <div v-if="showConfirmModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70" @click.self="closeConfirmModal">
      <div class="bg-gray-800 rounded-lg max-w-md w-full p-6 border-2 border-primary-500">
        <div class="flex items-center gap-3 mb-4">
          <span class="text-3xl">🍳</span>
          <h3 class="text-xl font-bold text-primary-400">确认生成菜谱</h3>
        </div>

        <div v-if="isParsingDish" class="text-center py-8">
          <div class="animate-spin text-4xl mb-4">🤖</div>
          <p class="text-gray-400">AI正在解析菜谱所需食材...</p>
        </div>

        <div v-else-if="parsedDishInfo">
          <div class="mb-4">
            <p class="text-gray-300 mb-2">菜谱名称：<span class="text-primary-400 font-bold">{{ parsedDishInfo.name }}</span></p>
            <p class="text-gray-400 text-sm mb-3">{{ parsedDishInfo.description }}</p>
          </div>

          <div class="mb-4">
            <p class="text-sm text-gray-400 mb-2">所需食材：</p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="ingredient in parsedDishInfo.ingredients"
                :key="ingredient"
                class="px-3 py-1 bg-primary-500/20 text-primary-400 rounded-full text-sm"
              >
                {{ ingredient }}
              </span>
            </div>
          </div>

          <div class="flex gap-3">
            <button
              @click="closeConfirmModal"
              class="flex-1 px-4 py-3 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition"
            >
              取消
            </button>
            <button
              @click="confirmGenerate"
              class="flex-1 px-4 py-3 bg-primary-500 text-gray-900 rounded-lg hover:bg-primary-400 transition font-medium"
            >
              立即生成
            </button>
          </div>
        </div>

        <div v-else class="text-center py-4">
          <p class="text-red-400">解析失败，请重试</p>
          <button
            @click="closeConfirmModal"
            class="mt-4 px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import NavigationBar from '@/components/NavigationBar.vue'
import { recipeApi } from '@/services/recipeApi'

const router = useRouter()

// 搜索状态
const searchQuery = ref('')
const selectedIngredients = ref<string[]>([])
const searchResults = ref<any[]>([])
const isSearching = ref(false)
const hasSearched = ref(false)
const sortBy = ref('relevance')

// 建议和推荐
const suggestions = ref<string[]>([])
const showSuggestions = ref(false)
const aiRecommendation = ref<any>(null)
const isLoadingRecommendation = ref(false)

// 确认弹窗
const showConfirmModal = ref(false)
const isParsingDish = ref(false)
const parsedDishInfo = ref<any>(null)

// 热门搜索
const popularSearches = [
  '番茄鸡蛋', '宫保鸡丁', '红烧肉', '麻婆豆腐',
  '糖醋排骨', '鱼香肉丝', '青椒肉丝', '酸辣土豆丝',
  '西红柿炒蛋', '蒜蓉西兰花', '清蒸鱼', '炒青菜'
]

// 常见食材库（用于搜索建议）
const commonIngredients = [
  '番茄', '鸡蛋', '土豆', '牛肉', '猪肉', '鸡肉', '鱼', '虾',
  '豆腐', '青菜', '白菜', '萝卜', '茄子', '黄瓜', '西兰花', '菠菜',
  '洋葱', '大蒜', '生姜', '辣椒', '香菇', '木耳', '豆角', '芹菜'
]

/**
 * 处理输入变化
 */
function handleInputChange() {
  if (searchQuery.value.trim().length > 0) {
    // 生成搜索建议
    suggestions.value = commonIngredients
      .filter(ing => ing.includes(searchQuery.value.trim()))
      .slice(0, 8)
    showSuggestions.value = true
  } else {
    showSuggestions.value = false
  }
}

/**
 * 选择建议
 */
function selectSuggestion(suggestion: string) {
  if (!selectedIngredients.value.includes(suggestion)) {
    selectedIngredients.value.push(suggestion)
  }
  searchQuery.value = ''
  showSuggestions.value = false
}

/**
 * 添加食材
 */
function addIngredient(ingredient: string) {
  if (!selectedIngredients.value.includes(ingredient)) {
    selectedIngredients.value.push(ingredient)
  }
}

/**
 * 移除食材
 */
function removeIngredient(index: number) {
  selectedIngredients.value.splice(index, 1)
  
  // 如果没有食材了，清空搜索结果
  if (selectedIngredients.value.length === 0) {
    searchResults.value = []
    hasSearched.value = false
    aiRecommendation.value = null
  }
}

/**
 * 清空食材
 */
function clearIngredients() {
  selectedIngredients.value = []
  searchResults.value = []
  hasSearched.value = false
  aiRecommendation.value = null
}

/**
 * 处理搜索
 */
async function handleSearch() {
  const query = searchQuery.value.trim()
  
  if (query) {
    // 添加到已选食材
    if (!selectedIngredients.value.includes(query)) {
      selectedIngredients.value.push(query)
    }
    searchQuery.value = ''
  }
  
  if (selectedIngredients.value.length === 0) {
    return
  }
  
  isSearching.value = true
  hasSearched.value = true
  showSuggestions.value = false
  
  try {
    // 调用搜索API
    const results = await recipeApi.searchByIngredients(selectedIngredients.value)
    searchResults.value = results
  } catch (error) {
    console.error('搜索失败:', error)
    searchResults.value = []
  } finally {
    isSearching.value = false
  }
}

/**
 * 获取AI推荐
 */
async function getAIRecommendation() {
  if (selectedIngredients.value.length === 0) return
  
  isLoadingRecommendation.value = true
  
  try {
    const recommendation = await recipeApi.getIngredientRecommendation(selectedIngredients.value)
    aiRecommendation.value = recommendation
  } catch (error) {
    console.error('获取AI推荐失败:', error)
  } finally {
    isLoadingRecommendation.value = false
  }
}

/**
 * 直接生成菜谱
 */
function generateRecipeDirectly() {
  // 跳转到主页并传递食材
  router.push({
    path: '/',
    query: {
      ingredients: selectedIngredients.value.join(',')
    }
  })
}

/**
 * 查看菜谱详情
 */
function viewRecipe(recipe: any) {
  if (recipe.id) {
    router.push(`/recipe/${recipe.id}`)
  }
}

/**
 * 排序后的结果
 */
const sortedResults = computed(() => {
  const results = [...searchResults.value]
  
  switch (sortBy.value) {
    case 'difficulty':
      return results.sort((a, b) => {
        const order: Record<string, number> = { easy: 1, medium: 2, hard: 3 }
        return order[a.difficulty] - order[b.difficulty]
      })
    case 'time':
      return results.sort((a, b) => a.cooking_time - b.cooking_time)
    case 'relevance':
    default:
      return results.sort((a, b) => b.matchScore - a.matchScore)
  }
})

/**
 * 处理推荐菜谱点击
 */
async function handleDishClick(dishName: string) {
  showConfirmModal.value = true
  isParsingDish.value = true
  parsedDishInfo.value = null
  
  try {
    // 调用AI解析菜谱所需食材
    const result = await recipeApi.parseDishIngredients(dishName)
    parsedDishInfo.value = result
  } catch (error) {
    console.error('解析菜谱失败:', error)
  } finally {
    isParsingDish.value = false
  }
}

/**
 * 关闭确认弹窗
 */
function closeConfirmModal() {
  showConfirmModal.value = false
  parsedDishInfo.value = null
}

/**
 * 确认生成菜谱
 */
function confirmGenerate() {
  if (parsedDishInfo.value && parsedDishInfo.value.ingredients) {
    // 跳转到主页并传递食材
    router.push({
      path: '/',
      query: {
        ingredients: parsedDishInfo.value.ingredients.join(','),
        recipeName: parsedDishInfo.value.name
      }
    })
  }
  closeConfirmModal()
}
</script>
