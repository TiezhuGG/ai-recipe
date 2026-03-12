<template>
  <div class="multi-selector">
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-3">
      {{ label }}
    </label>
    
    <div class="flex flex-wrap gap-2">
      <button
        v-for="option in options"
        :key="option"
        @click="toggleOption(option)"
        :class="[
          'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
          'border-2 min-w-[80px]',
          isSelected(option)
            ? 'bg-primary-500 text-white border-primary-500 shadow-md'
            : 'bg-white text-gray-700 border-gray-300 hover:border-primary-300 hover:bg-primary-50'
        ]"
        type="button"
      >
        {{ option }}
      </button>
    </div>

    <!-- 已选择提示 -->
    <p v-if="localSelectedOptions.length > 0" class="mt-3 text-sm text-gray-600">
      已选择 {{ localSelectedOptions.length }} 项
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Props
interface Props {
  label?: string
  options: string[]
  modelValue: string[]
}

const props = withDefaults(defineProps<Props>(), {
  label: '',
  modelValue: () => [],
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()


const localSelectedOptions = computed({
  get() {
    return props.modelValue
  },
  set(newValue: string[]) {
    emit('update:modelValue', newValue)
  }
})

// // 状态
// const selectedOptions = ref<string[]>([...props.modelValue])

// // 监听外部变化
// watch(
//   () => props.modelValue,
//   (newValue) => {
//     selectedOptions.value = [...newValue]
//   }
// )

// // 监听内部变化，同步到外部
// watch(
//   selectedOptions,
//   (newValue) => {
//     emit('update:modelValue', newValue)
//   },
//   { deep: true }
// )

/**
 * 检查选项是否被选中
 */
function isSelected(option: string): boolean {
  return localSelectedOptions.value.includes(option)
}

/**
 * 切换选项的选中状态
 */
function toggleOption(option: string) {
  const index = localSelectedOptions.value.indexOf(option)
  
  if (index > -1) {
    // 已选中，取消选择
    localSelectedOptions.value.splice(index, 1)
  } else {
    // 未选中，添加选择
    localSelectedOptions.value.push(option)
  }
}

/**
 * 清空所有选择
 */
function clearAll() {
  localSelectedOptions.value = []
}

// 暴露方法给父组件
defineExpose({
  clearAll,
})
</script>

<style scoped>
/* 组件样式已通过TailwindCSS实现 */
</style>
