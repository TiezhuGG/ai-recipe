<template>
  <div class="home-view">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      <h1 class="text-3xl sm:text-4xl font-bold text-center mb-4 sm:mb-8">AI智能菜谱生成平台</h1>
      <p class="text-center text-gray-600 mb-6 sm:mb-8 text-sm sm:text-base">
        一键生成专属菜谱，让每一餐都充满惊喜
      </p>
      
      <div class="grid lg:grid-cols-2 gap-6 lg:gap-8">
        <!-- 菜谱生成表单 -->
        <RecipeGeneratorForm @recipeGenerated="handleRecipeGenerated" />
        
        <!-- 菜谱展示 -->
        <RecipeDisplay 
          v-if="generatedRecipe" 
          :recipe="generatedRecipe"
          @saved="handleRecipeSaved"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import RecipeGeneratorForm from '@/components/RecipeGeneratorForm.vue'
import RecipeDisplay from '@/components/RecipeDisplay.vue'
import type { Recipe } from '@/types'

const generatedRecipe = ref<Recipe | null>(null)

function handleRecipeGenerated(recipe: Recipe) {
  generatedRecipe.value = recipe
}

function handleRecipeSaved(recipeId: string) {
  console.log('Recipe saved with ID:', recipeId)
}
</script>
