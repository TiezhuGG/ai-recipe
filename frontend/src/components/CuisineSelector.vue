<template>
  <MultiSelector
    label="菜系选择"
    :options="cuisineOptions"
    v-model="selectedCuisines"
  />
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import MultiSelector from './MultiSelector.vue'

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

// 菜系选项
const cuisineOptions = [
  // 中国八大菜系
  '川菜',
  '粤菜',
  '鲁菜',
  '苏菜',
  '浙菜',
  '闽菜',
  '湘菜',
  '徽菜',
  // 国际菜系
  '法餐',
  '意大利餐',
  '日本料理',
  '韩国料理',
  '泰国菜',
  '墨西哥菜',
  '西班牙菜',
  '印度菜',
]

const selectedCuisines = computed({
  get() {
    return props.modelValue
  },
  set(newValue: string[]) {
    emit('update:modelValue', newValue)
  }
})

// // 状态
// const selectedCuisines = ref<string[]>([...props.modelValue])

// // 监听外部变化
// watch(
//   () => props.modelValue,
//   (newValue) => {
//     selectedCuisines.value = [...newValue]
//   }
// )

// // 监听内部变化，同步到外部
// watch(
//   selectedCuisines,
//   (newValue) => {
//     emit('update:modelValue', newValue)
//   },
//   { deep: true }
// )
</script>

<style scoped>
/* 组件样式已通过TailwindCSS实现 */
</style>
