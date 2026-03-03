<template>
  <div class="recipe-detail-view">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      <!-- 返回按钮 -->
      <button 
        @click="router.back()"
        class="mb-4 sm:mb-6 flex items-center gap-2 text-gray-600 hover:text-gray-800 transition touch-target"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        返回
      </button>

      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-12">
        <svg class="animate-spin h-10 w-10 sm:h-12 sm:w-12 mx-auto text-primary-500" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-4 text-gray-600 text-sm sm:text-base">加载中...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="text-center py-12">
        <svg class="w-14 h-14 sm:w-16 sm:h-16 mx-auto text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="mt-4 text-gray-600 text-sm sm:text-base">{{ error }}</p>
      </div>

      <!-- 菜谱详情 -->
      <RecipeDisplay v-else :recipe="recipe" @saved="handleRecipeSaved" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import RecipeDisplay from '@/components/RecipeDisplay.vue'
import { recipeApi } from '@/services/recipeApi'
import type { Recipe } from '@/types'

const route = useRoute()
const router = useRouter()
const recipeId = route.params.id as string

const recipe = ref<Recipe | null>(null)
const loading = ref(false)
const error = ref('')

onMounted(async () => {
  await loadRecipe()
})

async function loadRecipe() {
  loading.value = true
  error.value = ''
  
  try {
    recipe.value = await recipeApi.getRecipeById(recipeId)
  } catch (err: any) {
    error.value = err.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function handleRecipeSaved(savedRecipeId: string) {
  console.log('Recipe saved with ID:', savedRecipeId)
}
</script>
