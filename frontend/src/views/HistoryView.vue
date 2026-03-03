<template>
  <div class="history-view">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      <h1 class="text-2xl sm:text-3xl font-bold mb-6 sm:mb-8">我的菜谱历史</h1>
      
      <RecipeHistory @selectRecipe="handleSelectRecipe" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import RecipeHistory from '@/components/RecipeHistory.vue'

const router = useRouter()

function handleSelectRecipe(recipeId: string) {
  router.push(`/recipe/${recipeId}`)
}
</script>
