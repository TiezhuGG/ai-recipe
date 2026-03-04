<template>
  <div class="ingredient-input">
    <label class="block text-sm font-medium text-gray-700 mb-2">
      食材输入
      <span class="text-gray-500 text-xs ml-2">（用逗号分隔多个食材）</span>
    </label>
    
    <!-- 输入框 -->
    <div class="relative">
      <input
        v-model="inputValue"
        type="text"
        placeholder="例如：鸡胸肉, 西兰花, 胡萝卜"
        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
        @keydown.enter="handleAdd"
        @blur="handleAdd"
      />
      <button
        v-if="inputValue.trim()"
        @click="handleAdd"
        class="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-1.5 bg-primary-500 text-white text-sm rounded-md hover:bg-primary-600 transition"
      >
        添加
      </button>
    </div>

    <!-- 验证错误提示 -->
    <p v-if="validationError" class="mt-2 text-sm text-red-600">
      {{ validationError }}
    </p>

    <!-- 食材标签列表 -->
    <div v-if="ingredients.length > 0" class="mt-4 flex flex-wrap gap-2">
      <div
        v-for="(ingredient, index) in ingredients"
        :key="index"
        class="inline-flex items-center gap-2 px-3 py-1.5 bg-primary-50 text-primary-700 rounded-full text-sm"
      >
        <span>{{ ingredient }}</span>
        <button
          @click="removeIngredient(index)"
          class="hover:bg-primary-100 rounded-full p-0.5 transition"
          :aria-label="`删除 ${ingredient}`"
        >
          <svg
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- 空状态提示 -->
    <p v-else class="mt-4 text-sm text-gray-500">
      还没有添加食材，请在上方输入框中添加
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

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

// 状态
const inputValue = ref('')
const ingredients = ref<string[]>([...props.modelValue])
const validationError = ref('')

// // 监听外部变化
// watch(
//   () => props.modelValue,
//   (newValue) => {
//     localIngredients.value = [...newValue]
//   }
// )

// // 监听内部变化，同步到外部
// watch(
//   ingredients,
//   (newValue) => {
//     emit('update:modelValue', newValue)
//   },
//   { deep: true }
// )

// 使用可写的 computed 属性来同步 v-model
const localIngredients = computed({
  get() {
    return props.modelValue
  },
  set(newValue: string[]) {
    emit('update:modelValue', newValue)
  }
})

/**
 * 验证输入
 */
function validateInput(value: string): boolean {
  validationError.value = ''

  // 检查是否为空或仅包含空白字符
  if (!value || !value.trim()) {
    validationError.value = '食材名称不能为空'
    return false
  }

  return true
}

/**
 * 解析输入的食材字符串
 * 支持逗号分隔的多个食材
 */
function parseIngredients(input: string): string[] {
  return input
    .split(',')
    .map((item) => item.trim())
    .filter((item) => item.length > 0)
}

/**
 * 添加食材
 */
function handleAdd() {
  const value = inputValue.value.trim()

  if (!value) {
    return
  }

  if (!validateInput(value)) {
    return
  }

  // 解析输入（支持逗号分隔）
  const newIngredients = parseIngredients(value)

  // 过滤掉已存在的食材（去重）
  const uniqueIngredients = newIngredients.filter(
    (item) => !localIngredients.value.includes(item)
  )

  if (uniqueIngredients.length === 0) {
    validationError.value = '这些食材已经添加过了'
    return
  }

  // 添加到列表
  localIngredients.value.push(...uniqueIngredients)

  // 清空输入框
  inputValue.value = ''
  validationError.value = ''
}

/**
 * 删除食材
 */
function removeIngredient(index: number) {
  localIngredients.value.splice(index, 1)
}

/**
 * 清空所有食材
 */
function clearAll() {
  localIngredients.value = []
  inputValue.value = ''
  validationError.value = ''
}

// 暴露方法给父组件
defineExpose({
  clearAll,
})
</script>

<style scoped>
/* 组件样式已通过TailwindCSS实现 */
</style>
