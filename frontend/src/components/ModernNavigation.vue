<template>
  <nav class="sticky top-0 z-50 bg-white/80 dark:bg-dark-surface/80 backdrop-blur-md border-b border-primary-300 dark:border-dark-border">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-accent-500 to-accent-600 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-lg">AI</span>
          </div>
          <span class="text-xl font-semibold text-primary-800 dark:text-primary-100">智能菜谱</span>
        </router-link>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center gap-2">
          <router-link
            to="/"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            :class="isActive('/') ? 'bg-accent-500 text-white' : 'text-primary-600 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-dark-hover'"
          >
            🏠 主页
          </router-link>
          <router-link
            to="/blind-box"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            :class="isActive('/blind-box') ? 'bg-accent-500 text-white' : 'text-primary-600 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-dark-hover'"
          >
            🎁 美食盲盒
          </router-link>
          <router-link
            to="/history"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            :class="isActive('/history') ? 'bg-accent-500 text-white' : 'text-primary-600 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-dark-hover'"
          >
            📖 菜谱全集
          </router-link>
          <router-link
            to="/cooking-school"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            :class="isActive('/cooking-school') ? 'bg-accent-500 text-white' : 'text-primary-600 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-dark-hover'"
          >
            👨‍🍳 去学厨房
          </router-link>
          <router-link
            to="/search"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            :class="isActive('/search') ? 'bg-accent-500 text-white' : 'text-primary-600 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-dark-hover'"
          >
            🔍 随料大搜
          </router-link>
        </div>

        <!-- Mobile Menu Button -->
        <button
          @click="mobileMenuOpen = !mobileMenuOpen"
          class="md:hidden p-2 rounded-lg text-primary-600 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-dark-hover"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Mobile Navigation -->
      <div v-if="mobileMenuOpen" class="md:hidden py-4 space-y-2">
        <router-link
          to="/"
          @click="mobileMenuOpen = false"
          class="block px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="isActive('/') ? 'bg-accent-500 text-white' : 'text-primary-600 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-dark-hover'"
        >
          🏠 主页
        </router-link>
        <router-link
          to="/blind-box"
          @click="mobileMenuOpen = false"
          class="block px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="isActive('/blind-box') ? 'bg-accent-500 text-white' : 'text-primary-600 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-dark-hover'"
        >
          🎁 美食盲盒
        </router-link>
        <router-link
          to="/history"
          @click="mobileMenuOpen = false"
          class="block px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="isActive('/history') ? 'bg-accent-500 text-white' : 'text-primary-600 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-dark-hover'"
        >
          📖 菜谱全集
        </router-link>
        <router-link
          to="/cooking-school"
          @click="mobileMenuOpen = false"
          class="block px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="isActive('/cooking-school') ? 'bg-accent-500 text-white' : 'text-primary-600 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-dark-hover'"
        >
          👨‍🍳 去学厨房
        </router-link>
        <router-link
          to="/search"
          @click="mobileMenuOpen = false"
          class="block px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="isActive('/search') ? 'bg-accent-500 text-white' : 'text-primary-600 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-dark-hover'"
        >
          🔍 随料大搜
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const mobileMenuOpen = ref(false)

function isActive(path: string): boolean {
  return route.path === path
}
</script>
