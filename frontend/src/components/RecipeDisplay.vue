<template>
  <div v-if="recipe" class="recipe-display card-dark rounded-lg shadow-lg p-4 sm:p-6">
    <!-- 菜谱标题 -->
    <div class="mb-4 sm:mb-6">
      <h2 class="text-2xl sm:text-3xl font-bold text-primary-400 mb-2">{{ recipe.name }}</h2>
      <div class="flex flex-wrap gap-2 sm:gap-3 text-xs sm:text-sm">
        <span class="px-2 sm:px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full border border-blue-500/30">
          难度：{{ difficultyText }}
        </span>
        <span class="px-2 sm:px-3 py-1 bg-green-500/20 text-green-300 rounded-full border border-green-500/30">
          ⏱️ {{ recipe.cookingTime }} 分钟
        </span>
        <span class="px-2 sm:px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full border border-purple-500/30">
          👥 {{ recipe.servings }} 人份
        </span>
      </div>
    </div>

    <!-- 菜谱图片 -->
    <img
      v-if="recipe.image"
      :src="recipe.image"
      :alt="recipe.name"
      class="w-full h-48 sm:h-64 object-cover rounded-lg mb-4 sm:mb-6 img-optimized"
      loading="lazy"
    />

    <!-- 安全提示 -->
    <div v-if="recipe.safetyTips && recipe.safetyTips.length > 0" class="mb-4 sm:mb-6 p-3 sm:p-4 bg-orange-500/10 border-l-4 border-orange-500 rounded">
      <h3 class="font-semibold text-orange-400 mb-2 flex items-center gap-2 text-sm sm:text-base">
        <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        安全提示
      </h3>
      <ul class="space-y-1 text-xs sm:text-sm text-orange-300">
        <li v-for="(tip, index) in recipe.safetyTips" :key="index">• {{ tip }}</li>
      </ul>
    </div>

    <!-- 食材列表 -->
    <div class="mb-4 sm:mb-6">
      <h3 class="text-lg sm:text-xl font-semibold text-gray-200 mb-2 sm:mb-3">📝 所需食材</h3>
      <div class="grid sm:grid-cols-2 gap-3 sm:gap-4">
        <div v-if="recipe.ingredients.main.length > 0">
          <h4 class="font-medium text-primary-400 mb-2 text-sm sm:text-base">主料</h4>
          <ul class="space-y-1">
            <li v-for="(ing, index) in recipe.ingredients.main" :key="index" class="text-gray-300 text-xs sm:text-sm">
              • {{ ing.name }} {{ ing.amount }}{{ ing.unit }}
            </li>
          </ul>
        </div>
        <div v-if="recipe.ingredients.secondary.length > 0">
          <h4 class="font-medium text-primary-400 mb-2 text-sm sm:text-base">辅料</h4>
          <ul class="space-y-1">
            <li v-for="(ing, index) in recipe.ingredients.secondary" :key="index" class="text-gray-300 text-xs sm:text-sm">
              • {{ ing.name }} {{ ing.amount }}{{ ing.unit }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 烹饪步骤 -->
    <div class="mb-4 sm:mb-6">
      <h3 class="text-lg sm:text-xl font-semibold text-gray-200 mb-2 sm:mb-3">👨‍🍳 烹饪步骤</h3>
      <ol class="space-y-3 sm:space-y-4">
        <li v-for="step in recipe.steps" :key="step.order" class="flex gap-3 sm:gap-4">
          <span class="flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 bg-primary-500 text-dark-500 rounded-full flex items-center justify-center font-semibold text-sm sm:text-base">
            {{ step.order }}
          </span>
          <p class="flex-1 text-gray-300 pt-1 text-xs sm:text-sm">{{ step.description }}</p>
        </li>
      </ol>
    </div>

    <!-- 保存按钮 -->
    <button
      @click="handleSave"
      :disabled="saving"
      class="w-full py-3 px-4 sm:px-6 bg-green-600 text-white rounded-lg font-medium hover:bg-green-500 transition disabled:bg-gray-600 disabled:text-gray-400 touch-target text-sm sm:text-base shadow-lg"
    >
      {{ saving ? '保存中...' : '💾 保存菜谱' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { recipeApi } from '@/services/recipeApi'
import type { Recipe } from '@/types'

// Props
interface Props {
  recipe: Recipe | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'saved': [recipeId: string]
}>()

const saving = ref(false)

// 难度文本
const difficultyText = computed(() => {
  const map = { easy: '简单', medium: '中等', hard: '困难' }
  return props.recipe ? map[props.recipe.difficulty] : ''
})

/**
 * 保存菜谱
 */
async function handleSave() {
  if (!props.recipe) return

  saving.value = true
  try {
    const recipeId = await recipeApi.saveRecipe(props.recipe)
    emit('saved', recipeId)
    alert('菜谱保存成功！')
  } catch (err: any) {
    alert(err.message || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>
