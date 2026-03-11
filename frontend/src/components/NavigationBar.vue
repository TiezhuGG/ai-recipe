<template>
  <div class="flex items-center justify-between bg-dark-500 px-6 py-4 rounded-lg border-2 border-primary-500">
    <div class="flex items-center gap-3">
      <span class="text-3xl">{{ icon }}</span>
      <div>
        <h1 class="text-2xl font-bold text-primary-500">{{ title }}</h1>
        <p class="text-xs text-gray-400">{{ subtitle }}</p>
      </div>
    </div>
    
    <div class="flex gap-3">
      <button
        @click="$router.push('/')"
        :class="[
          'px-4 py-2 rounded-lg transition font-medium',
          currentRoute === 'home'
            ? 'bg-primary-500 text-dark-500 hover:bg-primary-400'
            : 'bg-dark-400 text-gray-300 hover:bg-dark-300 border border-gray-600'
        ]"
      >
        🏠 主页
      </button>
      <button
        @click="$router.push('/blind-box')"
        :class="[
          'px-4 py-2 rounded-lg transition font-medium',
          currentRoute === 'blind-box'
            ? 'bg-primary-500 text-dark-500 hover:bg-primary-400'
            : 'bg-dark-400 text-gray-300 hover:bg-dark-300 border border-gray-600'
        ]"
      >
        🎁 美食盲盒
      </button>
      <button
        @click="$router.push('/history')"
        :class="[
          'px-4 py-2 rounded-lg transition font-medium',
          currentRoute === 'history'
            ? 'bg-primary-500 text-dark-500 hover:bg-primary-400'
            : 'bg-dark-400 text-gray-300 hover:bg-dark-300 border border-gray-600'
        ]"
      >
        📖 菜谱全集
      </button>
      <button
        @click="$router.push('/cooking-school')"
        :class="[
          'px-4 py-2 rounded-lg transition font-medium',
          currentRoute === 'cooking-school'
            ? 'bg-primary-500 text-dark-500 hover:bg-primary-400'
            : 'bg-dark-400 text-gray-300 hover:bg-dark-300 border border-gray-600'
        ]"
      >
        👨‍🍳 去学厨房
      </button>
      <button
        @click="$router.push('/search')"
        :class="[
          'px-4 py-2 rounded-lg transition font-medium',
          currentRoute === 'search'
            ? 'bg-primary-500 text-dark-500 hover:bg-primary-400'
            : 'bg-dark-400 text-gray-300 hover:bg-dark-300 border border-gray-600'
        ]"
      >
        🔍 随料大搜
      </button>
      <button
        class="px-4 py-2 bg-dark-400 text-gray-300 rounded-lg hover:bg-dark-300 transition border border-gray-600"
      >
        ⋯ 更多
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  icon: string
  title: string
  subtitle: string
  currentRoute: 'home' | 'blind-box' | 'history' | 'cooking-school' | 'search'
}

defineProps<Props>()
</script>
