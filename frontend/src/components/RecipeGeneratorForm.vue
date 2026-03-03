<template>
  <div class="recipe-generator-form bg-white rounded-lg shadow-lg p-4 sm:p-6 space-y-4 sm:space-y-6">
    <h2 class="text-xl sm:text-2xl font-bold text-gray-800 mb-4 sm:mb-6">定制你的专属菜谱</h2>

    <!-- 食材输入 -->
    <IngredientInput v-model="formData.ingredients" />

    <!-- 口味选择 -->
    <FlavorSelector v-model="formData.flavorTags" />

    <!-- 菜系选择 -->
    <CuisineSelector v-model="formData.cuisineTypes" />

    <!-- 图片上传 -->
    <ImageUploader
      v-model="uploadedImage"
      @ingredientsRecognized="handleIngredientsRecognized"
    />

    <!-- 特殊人群 -->
    <SpecialGroupSelector v-model="formData.specialGroups" />

    <!-- 错误提示 -->
    <div v-if="error" class="p-3 sm:p-4 bg-red-50 border border-red-200 rounded-lg">
      <p class="text-xs sm:text-sm text-red-600">{{ error }}</p>
    </div>

    <!-- 生成按钮 -->
    <button
      @click="handleGenerate"
      :disabled="loading || !canGenerate"
      :class="[
        'w-full py-3 sm:py-4 px-4 sm:px-6 rounded-lg font-medium text-base sm:text-lg transition-all touch-target',
        loading || !canGenerate
          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
          : 'bg-primary-500 text-white hover:bg-primary-600 shadow-lg hover:shadow-xl'
      ]"
    >
      <span v-if="loading" class="flex items-center justify-center gap-2">
        <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        生成中...
      </span>
      <span v-else>🍳 生成菜谱</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import IngredientInput from './IngredientInput.vue'
import FlavorSelector from './FlavorSelector.vue'
import CuisineSelector from './CuisineSelector.vue'
import ImageUploader from './ImageUploader.vue'
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

// 其他状态（不需要持久化）
const uploadedImage = ref<File | null>(null)
const loading = ref(false)
const error = ref('')

// 识别的食材（临时状态，不持久化）
const recognizedIngredients = ref<string[]>([])

// 是否可以生成（至少有一个食材）
const canGenerate = computed(() => {
  return formData.value.ingredients.length > 0 || 
         recognizedIngredients.value.length > 0
})

/**
 * 处理图片识别的食材
 */
function handleIngredientsRecognized(ingredients: string[]) {
  recognizedIngredients.value = ingredients
}

/**
 * 生成菜谱
 */
async function handleGenerate() {
  if (!canGenerate.value) {
    error.value = '请至少输入一个食材或上传食材图片'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const recipe = await recipeApi.generateRecipe({
      ingredients: formData.value.ingredients,
      flavor_tags: formData.value.flavorTags,
      cuisine_types: formData.value.cuisineTypes,
      special_groups: formData.value.specialGroups,
      recognized_ingredients: recognizedIngredients.value,
    })

    emit('recipeGenerated', recipe)
  } catch (err: any) {
    error.value = err.message || '生成失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>
