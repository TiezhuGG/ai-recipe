<template>
  <div class="history-view min-h-screen bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900 py-8">
    <div class="container mx-auto px-4 max-w-6xl">
      <!-- 头部导航 -->
      <div class="mb-8">
        <NavigationBar
          icon="📖"
          title="菜谱全集"
          subtitle="查看所有保存的菜谱"
          current-route="history"
        />
      </div>
      
      <RecipeHistory @selectRecipe="handleSelectRecipe" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import NavigationBar from '@/components/NavigationBar.vue'
import RecipeHistory from '@/components/RecipeHistory.vue'

const router = useRouter()

function handleSelectRecipe(recipeId: string) {
  router.push(`/recipe/${recipeId}`)
}
</script>
