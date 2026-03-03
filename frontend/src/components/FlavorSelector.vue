<template>
  <MultiSelector
    label="口味偏好"
    :options="flavorOptions"
    v-model="selectedFlavors"
  />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
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

// 口味选项
const flavorOptions = [
  '中餐',
  '西餐',
  '日韩料理',
  '东南亚风味',
  '网红菜',
  '家常菜',
  '健康轻食',
  '快手菜',
  '下饭菜',
  '宴客菜',
]

// 状态
const selectedFlavors = ref<string[]>([...props.modelValue])

// 监听外部变化
watch(
  () => props.modelValue,
  (newValue) => {
    selectedFlavors.value = [...newValue]
  }
)

// 监听内部变化，同步到外部
watch(
  selectedFlavors,
  (newValue) => {
    emit('update:modelValue', newValue)
  },
  { deep: true }
)
</script>

<style scoped>
/* 组件样式已通过TailwindCSS实现 */
</style>
