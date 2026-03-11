<template>
  <SingleSelector
    label="菜系选择"
    :options="cuisineOptions"
    v-model="selectedCuisine"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SingleSelector from './SingleSelector.vue'

// Props
interface Props {
  modelValue: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string]
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

const selectedCuisine = computed({
  get() {
    return props.modelValue
  },
  set(newValue: string) {
    emit('update:modelValue', newValue)
  }
})
</script>
