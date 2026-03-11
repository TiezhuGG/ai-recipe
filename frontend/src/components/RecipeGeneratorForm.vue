<template>
  <div class="recipe-generator-form space-y-6">
    <!-- 步骤1: 输入食材 -->
    <div class="card-dark p-6">
      <div class="flex items-center gap-2 mb-4">
        <span class="bg-primary-500 text-dark-500 font-bold px-3 py-1 rounded-full text-sm">1</span>
        <h3 class="text-lg font-bold text-primary-500">输入食材</h3>
      </div>
      <IngredientSelector v-model="formData.ingredients" />
    </div>

    <!-- 步骤2: 选择菜系 -->
    <div class="card-dark p-6">
      <div class="flex items-center gap-2 mb-4">
        <span class="bg-green-500 text-white font-bold px-3 py-1 rounded-full text-sm">2</span>
        <h3 class="text-lg font-bold text-green-400">选择菜系</h3>
      </div>
      <div class="space-y-4">
        <FlavorSelector v-model="formData.flavorTags" />
        <CuisineSelector v-model="formData.cuisineTypes" />
      </div>
    </div>

    <!-- 步骤3: 突出人群 -->
    <div class="card-dark p-6">
      <div class="flex items-center gap-2 mb-4">
        <span class="bg-pink-500 text-white font-bold px-3 py-1 rounded-full text-sm">3</span>
        <h3 class="text-lg font-bold text-pink-400">突出人群</h3>
      </div>
      <SpecialGroupSelector v-model="formData.specialGroups" />
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="p-4 bg-red-900/50 border border-red-500 rounded-lg">
      <p class="text-sm text-red-300">{{ error }}</p>
    </div>

    <!-- 生成按钮 -->
    <button
      @click="handleGenerate"
      :disabled="loading || !canGenerate"
      :class="[
        'w-full py-4 px-6 rounded-lg font-bold text-lg transition-all flex items-center justify-center gap-2',
        loading || !canGenerate
          ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
          : 'bg-primary-500 text-dark-500 hover:bg-primary-400 shadow-lg hover:shadow-xl'
      ]"
    >
      <svg v-if="loading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span v-if="loading">生成菜谱中...</span>
      <span v-else>✨ 交给大厨</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import IngredientSelector from './IngredientSelector.vue'
import FlavorSelector from './FlavorSelector.vue'
import CuisineSelector from './CuisineSelector.vue'
import SpecialGroupSelector from './SpecialGroupSelector.vue'
import { recipeApi } from '@/services/recipeApi'
import { useFormPersistence } from '@/composables/useFormPersistence'
import type { Recipe } from '@/types'

// Emits
const emit = defineEmits<{
  'recipeGenerated': [recipe: Recipe]
}>()

// 使用表单持久化
const { formData } = useFormPersistence()

// 其他状态
const loading = ref(false)
const error = ref('')

// 是否可以生成（至少有一个食材）
const canGenerate = computed(() => {
  return formData.value.ingredients.length > 0
})

/**
 * 生成菜谱
 */
async function handleGenerate() {
  if (!canGenerate.value) {
    error.value = '请至少选择一个食材'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const recipe = await recipeApi.generateRecipe({
      ingredients: formData.value.ingredients,
      flavor_tags: formData.value.flavorTags ? [formData.value.flavorTags] : [],
      cuisine_types: formData.value.cuisineTypes ? [formData.value.cuisineTypes] : [],
      special_groups: formData.value.specialGroups,
      recognized_ingredients: [],
    })

    emit('recipeGenerated', recipe)
  } catch (err: any) {
    error.value = err.message || '生成失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>
