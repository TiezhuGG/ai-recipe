<template>
  <div class="ingredient-selector space-y-4">
    <div class="text-center mb-4">
      <div class="text-5xl mb-2">🥬</div>
      <h3 class="text-xl font-bold text-gray-300 mb-1">添加食材</h3>
      <p class="text-sm text-gray-500">输入你有的食材，按回车添加</p>
      <p class="text-xs text-gray-600">支持肉类、蔬菜、海鲜等10种</p>
    </div>

    <!-- 已选食材显示 -->
    <div v-if="selectedIngredients.length > 0" class="flex flex-wrap gap-2 p-4 card-section rounded-lg mb-4">
      <span
        v-for="(ingredient, index) in selectedIngredients"
        :key="index"
        class="inline-flex items-center gap-1 px-3 py-1 bg-primary-500 text-dark-500 rounded-full text-sm font-medium"
      >
        {{ ingredient }}
        <button
          type="button"
          @click="removeIngredient(index)"
          class="hover:text-dark-300"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </span>
    </div>

    <!-- 输入框和按钮 -->
    <div class="mb-4 space-y-2 sm:flex sm:items-stretch sm:gap-2 sm:space-y-0">
      <input
        v-model="inputText"
        @keyup.enter="addFromInput"
        type="text"
        placeholder="输入食材名称，按回车添加"
        class="w-full px-4 py-3 bg-dark-400 border-2 border-gray-600 rounded-lg text-gray-200 placeholder-gray-500 focus:border-primary-500 focus:outline-none sm:flex-1"
      />
      <div class="grid grid-cols-2 gap-2 sm:flex sm:shrink-0">
        <button
          type="button"
          @click="addFromInput"
          class="w-full px-6 py-3 bg-primary-500 text-dark-500 rounded-lg hover:bg-primary-400 transition font-medium"
        >
          确定
        </button>
        <button
          type="button"
          @click="triggerImageUpload"
          class="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-3 text-white transition hover:bg-blue-500"
        >
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </button>
      </div>
      <input
        ref="fileInput"
        type="file"
        accept="image/jpeg,image/png,image/webp"
        @change="handleImageUpload"
        class="hidden"
      />
    </div>

    <!-- 预设食材分类（可折叠） -->
    <div class="space-y-2">
      <button
        type="button"
        @click="showPresets = !showPresets"
        class="flex items-center justify-between w-full px-4 py-3 card-section hover:bg-dark-300 rounded-lg transition"
      >
        <span class="text-sm font-medium text-gray-300">🍖 快速选择食材</span>
        <svg
          :class="['w-5 h-5 transition-transform text-primary-500', showPresets ? 'rotate-180' : '']"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <div v-show="showPresets" class="space-y-3 pt-2">
        <div v-for="category in ingredientCategories" :key="category.name" class="card-section p-3 rounded-lg">
          <h4 class="text-sm font-medium text-gray-400 mb-2">{{ category.name }}</h4>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="item in category.items"
              :key="item"
              type="button"
              @click="togglePresetIngredient(item)"
              :class="[
                'px-3 py-1 rounded-lg text-sm transition-all font-medium',
                selectedIngredients.includes(item)
                  ? 'bg-primary-500 text-dark-500'
                  : 'bg-dark-400 text-gray-300 hover:bg-dark-300'
              ]"
            >
              {{ item }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传进度 -->
    <div v-if="uploading" class="text-center py-6 card-section rounded-lg">
      <svg class="animate-spin h-10 w-10 mx-auto text-primary-500" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="mt-3 text-sm text-gray-400">AI识别中...</p>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="p-3 bg-red-900/50 border border-red-500 rounded-lg">
      <p class="text-sm text-red-300">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { recipeApi } from '@/services/recipeApi'

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
const selectedIngredients = computed({
  get() {
    return props.modelValue
  },
  set(newValue: string[]) {
    emit('update:modelValue', newValue)
  }
})
const inputText = ref('')
const fileInput = ref<HTMLInputElement>()
const uploading = ref(false)
const error = ref('')

// 预设食材分类
const ingredientCategories = [
  {
    name: '肉类',
    items: ['牛肉', '羊肉', '猪肉', '鸡胸肉', '鸡腿肉', '鸡翅', '鸭肉', '鹅肉', '排骨', '五花肉', '里脊肉', '牛腩', '羊排', '猪蹄', '鸡爪', '猪肝', '鸡心', '牛舌']
  },
  {
    name: '海鲜',
    items: ['虾', '大虾', '基围虾', '龙虾', '鱼', '鲈鱼', '三文鱼', '鳕鱼', '带鱼', '黄花鱼', '螃蟹', '鱿鱼', '章鱼', '扇贝', '蛤蜊', '生蚝', '海参', '鲍鱼', '海带', '紫菜']
  },
  {
    name: '蔬菜',
    items: ['土豆', '番茄', '黄瓜', '茄子', '青椒', '红椒', '尖椒', '胡萝卜', '白菜', '大白菜', '娃娃菜', '西兰花', '菠菜', '芹菜', '生菜', '油菜', '空心菜', '韭菜', '大葱', '洋葱', '蒜苗', '豆角', '四季豆', '豇豆', '莲藕', '山药', '南瓜', '冬瓜', '丝瓜', '苦瓜', '西葫芦', '玉米', '青笋', '莴笋', '芦笋', '花菜', '包菜', '紫甘蓝']
  },
  {
    name: '豆制品',
    items: ['豆腐', '嫩豆腐', '老豆腐', '豆腐皮', '豆腐干', '豆干', '腐竹', '豆芽', '黄豆芽', '绿豆芽', '千张', '豆泡', '油豆腐']
  },
  {
    name: '蛋类',
    items: ['鸡蛋', '鸭蛋', '鹅蛋', '鹌鹑蛋', '皮蛋', '咸蛋']
  },
  {
    name: '菌菇',
    items: ['香菇', '金针菇', '平菇', '杏鲍菇', '木耳', '银耳', '茶树菇', '口蘑', '草菇', '猴头菇', '竹荪', '松茸']
  },
  {
    name: '主食',
    items: ['米饭', '面条', '面粉', '饺子皮', '馄饨皮', '年糕', '粉丝', '粉条', '米粉', '河粉', '意大利面', '通心粉']
  },
  {
    name: '调味料',
    items: ['生姜', '大蒜', '小葱', '香菜', '八角', '花椒', '辣椒', '干辣椒', '豆瓣酱', '蚝油', '生抽', '老抽', '料酒', '醋', '糖', '盐', '鸡精', '味精', '胡椒粉', '五香粉', '孜然', '芝麻', '花生']
  }
]

const showPresets = ref(false)

/**
 * 从输入框添加食材
 */
function addFromInput() {
  if (!inputText.value.trim()) return

  const newIngredients = inputText.value
    .split(/[,，、]/)
    .map(item => item.trim())
    .filter(item => item && !selectedIngredients.value.includes(item))

  selectedIngredients.value = [...selectedIngredients.value, ...newIngredients]
  inputText.value = ''
}

/**
 * 切换预设食材
 */
function togglePresetIngredient(ingredient: string) {
  if (selectedIngredients.value.includes(ingredient)) {
    selectedIngredients.value = selectedIngredients.value.filter(item => item !== ingredient)
    return
  }

  selectedIngredients.value = [...selectedIngredients.value, ingredient]
}

/**
 * 移除食材
 */
function removeIngredient(index: number) {
  selectedIngredients.value = selectedIngredients.value.filter((_, itemIndex) => itemIndex !== index)
}

/**
 * 触发图片上传
 */
function triggerImageUpload() {
  fileInput.value?.click()
}

/**
 * 处理图片上传
 */
async function handleImageUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return

  // 验证文件
  const validTypes = ['image/jpeg', 'image/png', 'image/webp']
  if (!validTypes.includes(file.type)) {
    error.value = '只支持 JPEG、PNG 和 WebP 格式的图片'
    return
  }

  if (file.size > 10 * 1024 * 1024) {
    error.value = '图片大小不能超过 10MB'
    return
  }

  uploading.value = true
  error.value = ''

  try {
    const recognizedIngredients = await recipeApi.uploadImage(file)
    
    // 将识别结果按逗号、顿号等分隔符分割成多个食材
    const allIngredients: string[] = []
    recognizedIngredients.forEach(item => {
      const split = item.split(/[,，、]/).map(s => s.trim()).filter(s => s)
      allIngredients.push(...split)
    })
    
    // 添加识别的食材（去重）
    const newIngredients = allIngredients.filter(
      item => !selectedIngredients.value.includes(item)
    )
    selectedIngredients.value = [...selectedIngredients.value, ...newIngredients]
  } catch (err: any) {
    error.value = err.message || '识别失败，请重试'
  } finally {
    uploading.value = false
    // 清空文件输入
    if (target) target.value = ''
  }
}
</script>
