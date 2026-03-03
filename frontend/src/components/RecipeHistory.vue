<template>
  <div class="recipe-history">
    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-12">
      <svg class="animate-spin h-10 w-10 sm:h-12 sm:w-12 mx-auto text-primary-500" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="mt-4 text-gray-600 text-sm sm:text-base">加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="recipes.length === 0" class="text-center py-12">
      <svg class="w-20 h-20 sm:w-24 sm:h-24 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="mt-4 text-gray-600 text-sm sm:text-base">还没有保存的菜谱</p>
      <p class="mt-2 text-xs sm:text-sm text-gray-500">生成菜谱后点击保存即可查看历史记录</p>
    </div>

    <!-- 菜谱列表 -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
      <div
        v-for="recipe in recipes"
        :key="recipe.id"
        @click="$emit('selectRecipe', recipe.id)"
        class="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer overflow-hidden touch-target"
      >
        <div v-if="recipe.image" class="h-40 sm:h-48 bg-gray-200">
          <img :src="recipe.image" :alt="recipe.name" class="w-full h-full object-cover img-optimized" loading="lazy" />
        </div>
        <div class="p-3 sm:p-4">
          <h3 class="font-semibold text-base sm:text-lg text-gray-800 mb-2 line-clamp-2">{{ recipe.name }}</h3>
          <div class="flex flex-wrap gap-1.5 sm:gap-2 text-xs">
            <span class="px-2 py-1 bg-gray-100 text-gray-600 rounded">{{ difficultyMap[recipe.difficulty] }}</span>
            <span class="px-2 py-1 bg-gray-100 text-gray-600 rounded">{{ recipe.cookingTime }}分钟</span>
            <span class="px-2 py-1 bg-gray-100 text-gray-600 rounded">{{ recipe.servings}}人份</span>
          </div>
          <p v-if="recipe.createdAt" class="mt-2 text-xs text-gray-500">
            {{ formatDate(recipe.createdAt) }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { recipeApi } from '@/services/recipeApi'
import type { RecipeListItem } from '@/types'

// Emits
const emit = defineEmits<{
  'selectRecipe': [recipeId: string]
}>()

const recipes = ref<RecipeListItem[]>([])
const loading = ref(false)

const difficultyMap = { easy: '简单', medium: '中等', hard: '困难' }

onMounted(async () => {
  await loadRecipes()
})

async function loadRecipes() {
  loading.value = true
  try {
    const response = await recipeApi.getRecipeHistory()
    recipes.value = response.recipes
  } catch (err) {
    console.error('加载历史记录失败:', err)
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

defineExpose({ loadRecipes })
</script>
