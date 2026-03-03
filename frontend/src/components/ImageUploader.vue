<template>
  <div class="image-uploader">
    <label class="block text-sm font-medium text-gray-700 mb-3">
      上传食材图片
      <span class="text-gray-500 text-xs ml-2">（AI将自动识别图片中的食材）</span>
    </label>

    <!-- 上传区域 -->
    <div
      @click="triggerFileInput"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
      :class="[
        'border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all',
        isDragging
          ? 'border-primary-500 bg-primary-50'
          : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
      ]"
    >
      <!-- 预览图片 -->
      <div v-if="previewUrl" class="relative inline-block">
        <img
          :src="previewUrl"
          alt="预览图片"
          class="max-w-full max-h-64 rounded-lg shadow-md"
        />
        <button
          @click.stop="clearImage"
          class="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition shadow-lg"
          aria-label="删除图片"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <!-- 上传提示 -->
      <div v-else class="py-8">
        <svg
          class="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
        <p class="mt-2 text-sm text-gray-600">
          点击或拖拽图片到此处上传
        </p>
        <p class="mt-1 text-xs text-gray-500">
          支持 JPEG、PNG、WebP 格式，最大 10MB
        </p>
      </div>
    </div>

    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInputRef"
      type="file"
      accept="image/jpeg,image/jpg,image/png,image/webp"
      @change="handleFileSelect"
      class="hidden"
    />

    <!-- 上传进度 -->
    <div v-if="uploading" class="mt-4">
      <div class="flex items-center justify-between text-sm text-gray-600 mb-2">
        <span>正在识别食材...</span>
        <span>{{ uploadProgress }}%</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div
          class="bg-primary-500 h-2 rounded-full transition-all duration-300"
          :style="{ width: `${uploadProgress}%` }"
        ></div>
      </div>
    </div>

    <!-- 错误提示 -->
    <p v-if="error" class="mt-3 text-sm text-red-600">
      {{ error }}
    </p>

    <!-- 识别结果 -->
    <div v-if="recognizedIngredients.length > 0" class="mt-4">
      <p class="text-sm font-medium text-gray-700 mb-2">
        识别到的食材：
      </p>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="(ingredient, index) in recognizedIngredients"
          :key="index"
          class="px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm"
        >
          {{ ingredient }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { recipeApi } from '@/services/recipeApi'

// Props
interface Props {
  modelValue?: File | null
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: File | null]
  'ingredientsRecognized': [ingredients: string[]]
}>()

// 状态
const fileInputRef = ref<HTMLInputElement | null>(null)
const previewUrl = ref<string>('')
const isDragging = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const error = ref('')
const recognizedIngredients = ref<string[]>([])

// 最大文件大小（10MB）
const MAX_FILE_SIZE = 10 * 1024 * 1024

// 支持的文件类型
const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']

/**
 * 触发文件选择
 */
function triggerFileInput() {
  fileInputRef.value?.click()
}

/**
 * 验证文件
 */
function validateFile(file: File): boolean {
  error.value = ''

  // 验证文件类型
  if (!ALLOWED_TYPES.includes(file.type)) {
    error.value = '不支持的文件格式。请上传 JPEG、PNG 或 WebP 格式的图片'
    return false
  }

  // 验证文件大小
  if (file.size > MAX_FILE_SIZE) {
    const sizeMB = (file.size / (1024 * 1024)).toFixed(2)
    error.value = `文件过大 (${sizeMB}MB)。最大允许 10MB`
    return false
  }

  return true
}

/**
 * 创建预览URL
 */
function createPreview(file: File) {
  // 清除旧的预览URL
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }

  // 创建新的预览URL
  previewUrl.value = URL.createObjectURL(file)
}

/**
 * 处理文件选择
 */
async function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (file) {
    await processFile(file)
  }
}

/**
 * 处理拖拽悬停
 */
function handleDragOver() {
  isDragging.value = true
}

/**
 * 处理拖拽离开
 */
function handleDragLeave() {
  isDragging.value = false
}

/**
 * 处理文件拖放
 */
async function handleDrop(event: DragEvent) {
  isDragging.value = false
  
  const file = event.dataTransfer?.files[0]
  if (file) {
    await processFile(file)
  }
}

/**
 * 处理文件（验证、预览、上传）
 */
async function processFile(file: File) {
  // 验证文件
  if (!validateFile(file)) {
    return
  }

  // 创建预览
  createPreview(file)

  // 更新父组件
  emit('update:modelValue', file)

  // 上传并识别
  await uploadAndRecognize(file)
}

/**
 * 上传图片并识别食材
 */
async function uploadAndRecognize(file: File) {
  uploading.value = true
  uploadProgress.value = 0
  error.value = ''
  recognizedIngredients.value = []

  try {
    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 200)

    // 调用API识别食材
    const ingredients = await recipeApi.uploadImage(file)

    // 完成进度
    clearInterval(progressInterval)
    uploadProgress.value = 100

    // 保存识别结果
    recognizedIngredients.value = ingredients

    // 通知父组件
    emit('ingredientsRecognized', ingredients)

    // 延迟隐藏进度条
    setTimeout(() => {
      uploading.value = false
      uploadProgress.value = 0
    }, 500)
  } catch (err: any) {
    error.value = err.message || '识别失败，请重试'
    uploading.value = false
    uploadProgress.value = 0
  }
}

/**
 * 清除图片
 */
function clearImage() {
  // 清除预览URL
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = ''
  }

  // 清除文件输入
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }

  // 清除状态
  error.value = ''
  recognizedIngredients.value = []
  uploading.value = false
  uploadProgress.value = 0

  // 更新父组件
  emit('update:modelValue', null)
}

// 组件卸载时清理
import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
})
</script>

<style scoped>
/* 组件样式已通过TailwindCSS实现 */
</style>
