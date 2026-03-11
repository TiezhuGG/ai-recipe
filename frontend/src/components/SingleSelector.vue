<template>
  <div class="single-selector">
    <div class="flex flex-wrap gap-2">
      <button
        v-for="option in options"
        :key="option"
        @click="selectOption(option)"
        :class="[
          'px-4 py-2 rounded-lg text-sm font-medium transition-all',
          modelValue === option
            ? 'bg-primary-500 text-dark-500 shadow-lg'
            : 'bg-dark-400 text-gray-300 hover:bg-dark-300 border border-gray-600'
        ]"
      >
        {{ option }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// Props
interface Props {
  label: string
  options: string[]
  modelValue: string
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

/**
 * 选择选项
 */
function selectOption(option: string) {
  // 如果点击已选中的选项，则取消选择
  if (props.modelValue === option) {
    emit('update:modelValue', '')
  } else {
    emit('update:modelValue', option)
  }
}
</script>
