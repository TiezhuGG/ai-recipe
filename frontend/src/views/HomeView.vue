<template>
  <div class="home-view min-h-screen bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900 py-8">
    <div class="container mx-auto px-4 max-w-6xl">
      <!-- 头部导航 -->
      <div class="mb-8">
        <NavigationBar
          icon="🍳"
          title="AI菜谱平台"
          subtitle="百菜食谱，魔了or爱了！"
          current-route="home"
        />
      </div>

      <!-- 主要内容区域 -->
      <div class="flex flex-col">
          <RecipeGeneratorForm @recipeGenerated="handleRecipeGenerated" />

          <div class="mt-5">

            <RecipeDisplay 
            v-if="generatedRecipe" 
            :recipe="generatedRecipe"
            @saved="handleRecipeSaved"
            />
            
            <div v-else class="card-dark p-12 text-center">
              <div class="text-6xl mb-4">⭐</div>
              <h3 class="text-xl font-bold text-primary-500 mb-2">等待魔法发生...</h3>
              <p class="text-gray-400 text-sm">添加食材并选择菜系开始烹饪</p>
            </div>
          </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import NavigationBar from '@/components/NavigationBar.vue'
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
