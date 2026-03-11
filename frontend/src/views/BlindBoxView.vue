<template>
  <div class="blind-box-view min-h-screen bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900 dark:from-blue-900 dark:via-indigo-900 dark:to-purple-900 light:from-blue-50 light:via-indigo-50 light:to-purple-50 py-8">
    <div class="container mx-auto px-4 max-w-6xl">
      <!-- 头部导航 -->
      <div class="mb-8">
        <NavigationBar
          icon="🎲"
          title="今日吃啥"
          subtitle="随意吧，魔了or爱了！"
          current-route="blind-box"
        />
      </div>

      <!-- 主内容区 -->
      <div v-if="!generatedRecipe" class="space-y-6">
        <!-- 今日推荐卡片 -->
        <div class="card-dark p-8">
          <div class="text-center mb-6">
            <div class="text-6xl mb-4">🎲</div>
            <h2 class="text-2xl font-bold text-primary-400 mb-2">准备好了吗？</h2>
            <p class="text-gray-400">开始随机选择</p>
          </div>

          <!-- 偏好设置 -->
          <div class="mb-6">
            <button
              @click="showPreferences = !showPreferences"
              class="flex items-center justify-between w-full px-4 py-3 bg-dark-400 hover:bg-dark-300 rounded-lg transition"
            >
              <span class="text-sm font-medium text-gray-300">🎯 偏好设置</span>
              <svg
                :class="['w-5 h-5 transition-transform text-primary-500', showPreferences ? 'rotate-180' : '']"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <div v-show="showPreferences" class="mt-4 space-y-4 p-4 bg-dark-400 rounded-lg">
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="pref in preferences"
                  :key="pref"
                  @click="togglePreference(pref)"
                  :class="[
                    'px-3 py-2 rounded-lg text-sm transition-all',
                    selectedPreferences.includes(pref)
                      ? 'bg-primary-500 text-dark-500 font-medium'
                      : 'bg-dark-300 text-gray-300 hover:bg-dark-200 border border-gray-600'
                  ]"
                >
                  {{ pref }}
                </button>
              </div>
            </div>
          </div>

          <!-- 推荐食材和主厨 -->
          <div v-if="hasGenerated" class="grid md:grid-cols-2 gap-6">
            <!-- 推荐食材 -->
            <div>
              <div class="flex items-center gap-2 mb-3">
                <span class="text-lg">🥬</span>
                <h3 class="text-lg font-bold text-green-400">推荐菜品 (6道)</h3>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div
                  v-for="(ingredient, index) in randomIngredients"
                  :key="index"
                  class="px-4 py-3 bg-dark-400 text-gray-300 rounded-lg text-center border-2 border-green-500/30"
                >
                  {{ ingredient }}
                </div>
              </div>
            </div>

            <!-- 推荐主厨 -->
            <div>
              <div class="flex items-center gap-2 mb-3">
                <span class="text-lg">👨‍🍳</span>
                <h3 class="text-lg font-bold text-pink-400">推荐主厨</h3>
              </div>
              <div class="p-4 bg-dark-400 rounded-lg border-2 border-pink-500/30">
                <div class="flex items-center gap-3 mb-2">
                  <span class="text-3xl">👨‍🍳</span>
                  <div>
                    <p class="text-primary-400 font-bold">{{ randomChef.name }}</p>
                    <p class="text-xs text-gray-400">{{ randomChef.specialty }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="flex gap-4 mt-6">
            <button
              v-if="!hasGenerated"
              @click="generateRandomSelection"
              :disabled="loading"
              class="flex-1 py-3 px-6 bg-green-600 text-white rounded-lg hover:bg-green-500 transition font-medium shadow-lg"
            >
              🎲 开始随机选择
            </button>
            <template v-else>
              <button
                @click="resetSelection"
                :disabled="loading"
                class="flex-1 py-3 px-6 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition font-medium"
              >
                🔄 重新选择
              </button>
              <button
                @click="generateRecipe"
                :disabled="loading"
                :class="[
                  'flex-1 py-3 px-6 rounded-lg font-medium transition',
                  loading
                    ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    : 'bg-green-600 text-white hover:bg-green-500 shadow-lg'
                ]"
              >
                <span v-if="loading">生成中...</span>
                <span v-else>✨ 生成菜谱</span>
              </button>
            </template>
          </div>

          <!-- 提示信息 -->
          <div class="mt-6 p-4 bg-primary-500/10 rounded-lg border border-primary-500/30">
            <p class="text-sm text-gray-300 text-center">
              👉 每次随机选择6种食材，让AI帮你决定今天吃什么！💕
            </p>
          </div>
        </div>
      </div>

      <!-- 生成的菜谱展示 -->
      <div v-else class="space-y-6">
        <!-- 专属菜谱标题 -->
        <div class="text-center">
          <div class="inline-flex items-center gap-2 bg-dark-500 px-6 py-3 rounded-full border-2 border-primary-500">
            <span class="text-2xl">📋</span>
            <h2 class="text-xl font-bold text-primary-400">专属菜谱</h2>
          </div>
        </div>

        <!-- 菜谱展示 -->
        <div class="card-dark p-6">
          <!-- 菜谱标题和基本信息 -->
          <div class="mb-6 pb-6 border-b border-gray-700">
            <h2 class="text-3xl font-bold text-primary-400 mb-4">{{ generatedRecipe.name }}</h2>
            <div class="flex flex-wrap gap-3 text-sm">
              <span class="px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full border border-blue-500/30">
                难度：{{ difficultyText }}
              </span>
              <span class="px-3 py-1 bg-green-500/20 text-green-300 rounded-full border border-green-500/30">
                ⏱️ {{ generatedRecipe.cookingTime }} 分钟
              </span>
              <span class="px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full border border-purple-500/30">
                👥 {{ generatedRecipe.servings }} 人份
              </span>
            </div>
          </div>

          <!-- 所需食材 -->
          <div class="mb-6">
            <div class="flex items-center gap-2 mb-3">
              <span class="text-xl">🥘</span>
              <h3 class="text-xl font-semibold text-gray-200">所需食材</h3>
            </div>
            <div class="grid sm:grid-cols-2 gap-4">
              <div v-if="generatedRecipe.ingredients.main.length > 0">
                <h4 class="font-medium text-primary-400 mb-2">主料</h4>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="(ing, index) in generatedRecipe.ingredients.main"
                    :key="index"
                    class="px-3 py-1 bg-primary-500/20 text-primary-300 rounded-lg text-sm border border-primary-500/30"
                  >
                    {{ ing.name }} {{ ing.amount }}{{ ing.unit }}
                  </span>
                </div>
              </div>
              <div v-if="generatedRecipe.ingredients.secondary.length > 0">
                <h4 class="font-medium text-primary-400 mb-2">辅料</h4>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="(ing, index) in generatedRecipe.ingredients.secondary"
                    :key="index"
                    class="px-3 py-1 bg-gray-600 text-gray-300 rounded-lg text-sm border border-gray-500"
                  >
                    {{ ing.name }} {{ ing.amount }}{{ ing.unit }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 制作步骤 -->
          <div class="mb-6">
            <div class="flex items-center gap-2 mb-3">
              <span class="text-xl">📝</span>
              <h3 class="text-xl font-semibold text-gray-200">制作步骤</h3>
            </div>
            <ol class="space-y-3">
              <li v-for="step in generatedRecipe.steps" :key="step.order" class="flex gap-3">
                <span class="flex-shrink-0 w-8 h-8 bg-primary-500 text-dark-500 rounded-full flex items-center justify-center font-bold">
                  {{ step.order }}
                </span>
                <p class="flex-1 text-gray-300 pt-1">{{ step.description }}</p>
              </li>
            </ol>
          </div>

          <!-- 菜品效果图 -->
          <div class="mb-6">
            <div class="flex items-center gap-2 mb-3">
              <span class="text-xl">🖼️</span>
              <h3 class="text-xl font-semibold text-gray-200">菜品效果图</h3>
            </div>
            
            <div v-if="generatedImage" class="relative">
              <img :src="generatedImage" :alt="generatedRecipe.name" class="w-full rounded-lg" />
            </div>
            <div v-else class="bg-dark-400 rounded-lg p-12 text-center border-2 border-dashed border-gray-600">
              <div class="text-5xl mb-4">📷</div>
              <p class="text-gray-400 mb-4">暂无效果图</p>
              <button
                @click="generateDishImage"
                :disabled="generatingImage"
                :class="[
                  'px-6 py-3 rounded-lg font-medium transition',
                  generatingImage
                    ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-500'
                ]"
              >
                <span v-if="generatingImage">生成中...</span>
                <span v-else>✨ 生成效果图</span>
              </button>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="flex gap-4">
            <button
              @click="resetBlindBox"
              class="flex-1 py-3 px-6 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition font-medium"
            >
              🔄 再来一次
            </button>
            <button
              @click="saveRecipe"
              :disabled="saving"
              class="flex-1 py-3 px-6 bg-green-600 text-white rounded-lg hover:bg-green-500 transition font-medium"
            >
              <span v-if="saving">保存中...</span>
              <span v-else>💾 保存菜谱</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import NavigationBar from '@/components/NavigationBar.vue'
import { recipeApi } from '@/services/recipeApi'
import type { Recipe } from '@/types'

// 状态
const showPreferences = ref(false)
const selectedPreferences = ref<string[]>([])
const randomIngredients = ref<string[]>([])
const randomChef = ref({ name: '', specialty: '' })
const generatedRecipe = ref<Recipe | null>(null)
const generatedImage = ref<string>('')
const loading = ref(false)
const generatingImage = ref(false)
const saving = ref(false)
const hasGenerated = ref(false) // 是否已生成随机选择

// 偏好选项
const preferences = ['微辣多', '素菜多', '肉类', '咸鲜']

// 所有可用食材
const allIngredients = [
  '鸡腿菇', '油豆腐', '马苏里拉奶酪', '奶酪', '柚子', '鸡蛋',
  '牛肉', '羊肉', '猪肉', '鸡胸肉', '鸡翅', '鸭肉',
  '虾', '鱼', '螃蟹', '鱿鱼', '扇贝', '蛤蜊',
  '土豆', '番茄', '黄瓜', '茄子', '青椒', '胡萝卜',
  '豆腐', '豆腐皮', '豆芽', '腐竹', '千张',
  '香菇', '金针菇', '平菇', '杏鲍菇', '木耳',
  '米饭', '面条', '饺子皮', '年糕', '粉丝'
]

// 主厨列表
const chefs = [
  { name: '鲁菜大师', specialty: '擅长鲁菜，火候精准' },
  { name: '川菜大师', specialty: '擅长川菜，麻辣鲜香' },
  { name: '粤菜大师', specialty: '擅长粤菜，清淡鲜美' },
  { name: '湘菜大师', specialty: '擅长湘菜，香辣可口' },
  { name: '苏菜大师', specialty: '擅长苏菜，清鲜平和' }
]

// 难度文本
const difficultyText = computed(() => {
  const map = { easy: '简单', medium: '中等', hard: '困难' }
  return generatedRecipe.value ? map[generatedRecipe.value.difficulty] : ''
})

// 移除 onMounted 自动生成
// onMounted(() => {
//   generateRandomSelection()
// })

/**
 * 切换偏好
 */
function togglePreference(pref: string) {
  const index = selectedPreferences.value.indexOf(pref)
  if (index > -1) {
    selectedPreferences.value.splice(index, 1)
  } else {
    selectedPreferences.value.push(pref)
  }
}

/**
 * 生成随机选择
 */
function generateRandomSelection() {
  // 根据偏好筛选食材
  let availableIngredients = [...allIngredients]
  
  if (selectedPreferences.value.includes('素菜多')) {
    // 优先选择蔬菜类
    const veggies = allIngredients.filter(ing => 
      ['土豆', '番茄', '黄瓜', '茄子', '青椒', '胡萝卜', '豆腐', '豆芽', '香菇', '金针菇'].includes(ing)
    )
    availableIngredients = [...veggies, ...allIngredients]
  }
  
  if (selectedPreferences.value.includes('肉类')) {
    // 优先选择肉类
    const meats = allIngredients.filter(ing => 
      ['牛肉', '羊肉', '猪肉', '鸡胸肉', '鸡翅', '鸭肉', '虾', '鱼', '螃蟹'].includes(ing)
    )
    availableIngredients = [...meats, ...allIngredients]
  }
  
  // 随机选择6种食材
  const shuffled = [...availableIngredients].sort(() => 0.5 - Math.random())
  randomIngredients.value = shuffled.slice(0, 6)

  // 随机选择主厨
  randomChef.value = chefs[Math.floor(Math.random() * chefs.length)]
  
  hasGenerated.value = true
}

/**
 * 重新选择 - 清空所有内容
 */
function resetSelection() {
  randomIngredients.value = []
  randomChef.value = { name: '', specialty: '' }
  hasGenerated.value = false
}

/**
 * 生成菜谱
 */
async function generateRecipe() {
  loading.value = true
  
  try {
    const recipe = await recipeApi.generateRecipe({
      ingredients: randomIngredients.value,
      flavor_tags: selectedPreferences.value,
      cuisine_types: [],
      special_groups: [],
      recognized_ingredients: []
    })

    generatedRecipe.value = recipe
  } catch (err: any) {
    alert(err.message || '生成失败，请重试')
  } finally {
    loading.value = false
  }
}

/**
 * 生成菜品效果图
 */
async function generateDishImage() {
  if (!generatedRecipe.value) return

  generatingImage.value = true
  
  try {
    // 提取主要食材
    const mainIngredients = generatedRecipe.value.ingredients.main.map(ing => ing.name)
    
    // 调用API生成图片
    const imageUrl = await recipeApi.generateDishImage(
      generatedRecipe.value.name,
      mainIngredients
    )
    
    generatedImage.value = imageUrl
  } catch (err: any) {
    alert(err.message || '生成效果图失败')
  } finally {
    generatingImage.value = false
  }
}

/**
 * 保存菜谱
 */
async function saveRecipe() {
  if (!generatedRecipe.value) return

  saving.value = true
  
  try {
    await recipeApi.saveRecipe(generatedRecipe.value)
    alert('菜谱保存成功！')
  } catch (err: any) {
    alert(err.message || '保存失败')
  } finally {
    saving.value = false
  }
}

/**
 * 重置盲盒
 */
function resetBlindBox() {
  generatedRecipe.value = null
  generatedImage.value = ''
  resetSelection()
}
</script>
