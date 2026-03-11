<template>
  <SingleSelector
    label="口味偏好"
    :options="flavorOptions"
    v-model="selectedFlavor"
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

const selectedFlavor = computed({
  get() {
    return props.modelValue
  },
  set(newValue: string) {
    emit('update:modelValue', newValue)
  }
})
</script>
