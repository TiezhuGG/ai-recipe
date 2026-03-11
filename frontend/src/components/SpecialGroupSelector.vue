<template>
  <div class="special-group-selector">
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
      <button
        v-for="group in specialGroups"
        :key="group.value"
        @click="toggleGroup(group.value)"
        :class="[
          'flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all duration-200',
          isSelected(group.value)
            ? 'bg-primary-500/20 border-primary-500 shadow-lg'
            : 'bg-dark-400 border-gray-600 hover:border-primary-500/50 hover:bg-dark-300'
        ]"
        type="button"
      >
        <!-- 图标 -->
        <div
          :class="[
            'text-3xl mb-2',
            isSelected(group.value) ? 'opacity-100' : 'opacity-60'
          ]"
        >
          {{ group.icon }}
        </div>
        
        <!-- 标签 -->
        <span
          :class="[
            'text-sm font-medium',
            isSelected(group.value) ? 'text-primary-400' : 'text-gray-300'
          ]"
        >
          {{ group.label }}
        </span>
      </button>
    </div>

    <!-- 已选择提示和说明 -->
    <div v-if="localSelectedGroups.length > 0" class="mt-4 p-4 bg-primary-500/10 rounded-lg border border-primary-500/30">
      <div class="flex items-start gap-2">
        <svg class="w-5 h-5 text-primary-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
        </svg>
        <div class="flex-1">
          <p class="text-sm font-medium text-primary-300 mb-1">
            已选择：{{ selectedGroupLabels.join('、') }}
          </p>
          <p class="text-xs text-gray-400">
            系统将为您提供针对这些人群的饮食安全提示和注意事项
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Props
interface Props {
  modelValue: string[]
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

// 特殊人群选项
interface SpecialGroup {
  value: string
  label: string
  icon: string
}

const specialGroups: SpecialGroup[] = [
  { value: '小孩', label: '小孩', icon: '👶' },
  { value: '老人', label: '老人', icon: '👴' },
  { value: '孕妇', label: '孕妇', icon: '🤰' },
  { value: '糖尿病患者', label: '糖尿病', icon: '💉' },
  { value: '高血压患者', label: '高血压', icon: '❤️' },
  { value: '健身人群', label: '健身人群', icon: '💪' },
  { value: '素食者', label: '素食者', icon: '🥗' },
  { value: '过敏体质', label: '过敏体质', icon: '⚠️' },
]

const localSelectedGroups = computed({
  get() {
    return props.modelValue
  },
  set(newValue: string[]) {
    emit('update:modelValue', newValue)
  }
})

// // 状态
// const selectedGroups = ref<string[]>([...props.modelValue])

// 计算已选择的标签
const selectedGroupLabels = computed(() => {
  return localSelectedGroups.value.map(value => {
    const group = specialGroups.find(g => g.value === value)
    return group?.label || value
  })
})



// // 监听外部变化
// watch(
//   () => props.modelValue,
//   (newValue) => {
//     selectedGroups.value = [...newValue]
//   }
// )

// // 监听内部变化，同步到外部
// watch(
//   selectedGroups,
//   (newValue) => {
//     emit('update:modelValue', newValue)
//   },
//   { deep: true }
// )

/**
 * 检查人群是否被选中
 */
function isSelected(value: string): boolean {
  return localSelectedGroups.value.includes(value)
}

/**
 * 切换人群的选中状态
 */
function toggleGroup(value: string) {
  const index = localSelectedGroups.value.indexOf(value)
  
  if (index > -1) {
    // 已选中，取消选择
    localSelectedGroups.value.splice(index, 1)
  } else {
    // 未选中，添加选择
    localSelectedGroups.value.push(value)
  }
}

/**
 * 清空所有选择
 */
function clearAll() {
  localSelectedGroups.value = []
}

// 暴露方法给父组件
defineExpose({
  clearAll,
})
</script>

<style scoped>
/* 组件样式已通过TailwindCSS实现 */
</style>
