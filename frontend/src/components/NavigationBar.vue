<template>
  <div class="rounded-lg border-2 border-primary-500 bg-dark-500 px-4 py-4 sm:px-6">
    <div class="flex items-start justify-between gap-3 sm:items-center">
      <div class="flex min-w-0 items-center gap-3">
        <span class="shrink-0 text-3xl">{{ icon }}</span>
        <div class="min-w-0">
          <h1 class="break-words text-xl font-bold text-primary-500 sm:text-2xl">{{ title }}</h1>
          <p class="break-words text-xs leading-relaxed text-gray-400">{{ subtitle }}</p>
        </div>
      </div>

      <button
        type="button"
        class="inline-flex shrink-0 items-center gap-2 rounded-lg border border-gray-600 bg-dark-400 px-3 py-2 text-sm font-medium text-gray-300 transition hover:bg-dark-300 sm:hidden"
        @click="mobileMenuOpen = !mobileMenuOpen"
      >
        <span>{{ currentNavLabel }}</span>
        <svg
          :class="['h-4 w-4 transition-transform', mobileMenuOpen ? 'rotate-180' : '']"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
    </div>

    <div class="mt-4 hidden flex-wrap gap-3 sm:flex">
      <button
        v-for="item in navigationItems"
        :key="item.route"
        type="button"
        :class="navButtonClass(item.route)"
        @click="goTo(item.path)"
      >
        {{ item.label }}
      </button>
    </div>

    <div v-if="mobileMenuOpen" class="mt-4 grid gap-2 sm:hidden">
      <button
        v-for="item in navigationItems"
        :key="item.route"
        type="button"
        :class="mobileNavButtonClass(item.route)"
        @click="goTo(item.path)"
      >
        {{ item.label }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

type RouteName = 'home' | 'blind-box' | 'history' | 'cooking-school' | 'search'

interface Props {
  icon: string
  title: string
  subtitle: string
  currentRoute: RouteName
}

const props = defineProps<Props>()

const router = useRouter()
const mobileMenuOpen = ref(false)

const navigationItems: Array<{ route: RouteName; path: string; label: string }> = [
  { route: 'home', path: '/', label: '🏠 主页' },
  { route: 'blind-box', path: '/blind-box', label: '🎁 美食盲盒' },
  { route: 'history', path: '/history', label: '📖 菜谱全集' },
  { route: 'cooking-school', path: '/cooking-school', label: '👨‍🍳 去学厨房' },
  { route: 'search', path: '/search', label: '🔍 随料大搜' },
]

const currentNavLabel = computed(() => {
  return navigationItems.find(item => item.route === props.currentRoute)?.label ?? '导航'
})

function goTo(path: string) {
  mobileMenuOpen.value = false
  router.push(path)
}

function navButtonClass(route: RouteName) {
  return [
    'rounded-lg px-4 py-2 font-medium transition',
    props.currentRoute === route
      ? 'bg-primary-500 text-dark-500 hover:bg-primary-400'
      : 'border border-gray-600 bg-dark-400 text-gray-300 hover:bg-dark-300',
  ]
}

function mobileNavButtonClass(route: RouteName) {
  return [
    'w-full rounded-lg px-4 py-3 text-left text-sm font-medium transition',
    props.currentRoute === route
      ? 'bg-primary-500 text-dark-500 hover:bg-primary-400'
      : 'border border-gray-600 bg-dark-400 text-gray-300 hover:bg-dark-300',
  ]
}
</script>
