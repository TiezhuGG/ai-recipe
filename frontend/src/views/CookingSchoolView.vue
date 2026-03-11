<template>
  <div class="cooking-school-view min-h-screen bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900 py-8">
    <div class="container mx-auto px-4 max-w-6xl">
      <!-- 头部导航 -->
      <div class="mb-8">
        <NavigationBar
          icon="👨‍🍳"
          title="去学厨房"
          subtitle="AI烹饪导师，随时为你答疑解惑"
          current-route="cooking-school"
        />
      </div>

      <!-- 技巧详情模态框 -->
      <SkillDetailModal
        :show="showSkillModal"
        :skill="selectedSkill"
        @close="closeSkillModal"
      />

      <!-- 主内容区 -->
      <div class="grid lg:grid-cols-3 gap-6">
        <!-- 左侧：功能选择 -->
        <div class="lg:col-span-1 space-y-4">
          <!-- 功能卡片 -->
          <div class="card-dark p-6">
            <h2 class="text-xl font-bold text-primary-400 mb-4">🎓 学习模式</h2>
            <div class="space-y-3">
              <button
                v-for="mode in learningModes"
                :key="mode.id"
                @click="selectMode(mode.id)"
                :class="[
                  'w-full p-4 rounded-lg text-left transition-all',
                  selectedMode === mode.id
                    ? 'bg-primary-500 text-dark-500 shadow-lg'
                    : 'bg-dark-400 text-gray-300 hover:bg-dark-300'
                ]"
              >
                <div class="flex items-center gap-3">
                  <span class="text-2xl">{{ mode.icon }}</span>
                  <div>
                    <div class="font-medium">{{ mode.name }}</div>
                    <div class="text-xs opacity-80">{{ mode.description }}</div>
                  </div>
                </div>
              </button>
            </div>
          </div>

          <!-- 快速技巧 -->
          <div class="card-dark p-6">
            <h3 class="text-lg font-bold text-primary-400 mb-3">💡 今日技巧</h3>
            <div class="space-y-2">
              <div
                v-for="(tip, index) in dailyTips"
                :key="index"
                class="p-3 bg-dark-400 rounded-lg text-sm text-gray-300"
              >
                <div class="font-medium text-primary-300 mb-1">{{ tip.title }}</div>
                <div class="text-xs">{{ tip.content }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：主要内容区 -->
        <div class="lg:col-span-2">
          <!-- AI对话模式 -->
          <div v-if="selectedMode === 'chat'" class="card-dark p-6">
            <div class="flex items-center gap-3 mb-6">
              <span class="text-3xl">🤖</span>
              <div>
                <h2 class="text-2xl font-bold text-primary-400">AI烹饪导师</h2>
                <p class="text-sm text-gray-400">问我任何烹饪问题</p>
              </div>
            </div>

            <!-- 对话历史 -->
            <div class="mb-4 h-96 overflow-y-auto space-y-4 p-4 bg-dark-400 rounded-lg">
              <div v-if="chatHistory.length === 0" class="text-center text-gray-500 py-20">
                <div class="text-5xl mb-4">👋</div>
                <p>你好！我是你的AI烹饪导师</p>
                <p class="text-sm mt-2">问我任何关于烹饪的问题吧！</p>
              </div>
              
              <div
                v-for="(message, index) in chatHistory"
                :key="index"
                :class="[
                  'flex gap-3',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                ]"
              >
                <div
                  :class="[
                    'max-w-[80%] p-3 rounded-lg',
                    message.role === 'user'
                      ? 'bg-primary-500 text-dark-500'
                      : 'bg-gray-700 text-gray-200'
                  ]"
                >
                  <div class="text-sm whitespace-pre-wrap">{{ message.content }}</div>
                  <div class="text-xs opacity-70 mt-1">{{ message.time }}</div>
                </div>
              </div>
              
              <!-- 加载中 -->
              <div v-if="isThinking" class="flex gap-3 justify-start">
                <div class="bg-gray-700 text-gray-200 p-3 rounded-lg">
                  <div class="flex items-center gap-2">
                    <div class="animate-pulse">思考中</div>
                    <div class="flex gap-1">
                      <span class="animate-bounce">.</span>
                      <span class="animate-bounce" style="animation-delay: 0.1s">.</span>
                      <span class="animate-bounce" style="animation-delay: 0.2s">.</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 输入框 -->
            <div class="flex gap-3">
              <input
                v-model="userInput"
                @keyup.enter="sendMessage"
                type="text"
                placeholder="输入你的问题..."
                class="flex-1 px-4 py-3 bg-dark-400 border-2 border-gray-600 rounded-lg text-gray-200 placeholder-gray-500 focus:border-primary-500 focus:outline-none"
              />
              <button
                @click="sendMessage"
                :disabled="!userInput.trim() || isThinking"
                class="px-6 py-3 bg-primary-500 text-dark-500 rounded-lg hover:bg-primary-400 transition font-medium disabled:bg-gray-600 disabled:text-gray-400"
              >
                发送
              </button>
            </div>

            <!-- 快速问题 -->
            <div class="mt-4">
              <div class="text-sm text-gray-400 mb-2">快速提问：</div>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="question in quickQuestions"
                  :key="question"
                  @click="askQuickQuestion(question)"
                  class="px-3 py-1 bg-dark-400 text-gray-300 rounded-full text-sm hover:bg-dark-300 transition"
                >
                  {{ question }}
                </button>
              </div>
            </div>
          </div>

          <!-- 技巧知识库模式 -->
          <div v-else-if="selectedMode === 'skills'" class="card-dark p-6">
            <h2 class="text-2xl font-bold text-primary-400 mb-6">📚 烹饪技巧知识库</h2>
            
            <div class="grid md:grid-cols-2 gap-4">
              <div
                v-for="skill in cookingSkills"
                :key="skill.id"
                @click="viewSkillDetail(skill)"
                class="p-4 bg-dark-400 rounded-lg hover:bg-dark-300 cursor-pointer transition"
              >
                <div class="flex items-start gap-3">
                  <span class="text-3xl">{{ skill.icon }}</span>
                  <div class="flex-1">
                    <h3 class="font-bold text-primary-300 mb-1">{{ skill.title }}</h3>
                    <p class="text-sm text-gray-400">{{ skill.description }}</p>
                    <div class="mt-2 text-xs text-gray-500">
                      {{ skill.lessons }} 个课程
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 实时指导模式 -->
          <div v-else-if="selectedMode === 'guide'" class="card-dark p-6">
            <h2 class="text-2xl font-bold text-primary-400 mb-6">🎯 实时烹饪指导</h2>
            
            <div v-if="!selectedRecipe" class="text-center py-12">
              <div class="text-5xl mb-4">🍳</div>
              <p class="text-gray-400 mb-4">选择一个菜谱开始实时指导</p>
              <button
                @click="$router.push('/')"
                class="px-6 py-3 bg-primary-500 text-dark-500 rounded-lg hover:bg-primary-400 transition font-medium"
              >
                去生成菜谱
              </button>
            </div>

            <div v-else>
              <!-- 步骤指导 -->
              <div class="mb-6">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-xl font-bold text-gray-200">{{ selectedRecipe.name }}</h3>
                  <div class="text-sm text-gray-400">
                    步骤 {{ currentStep + 1 }} / {{ selectedRecipe.steps.length }}
                  </div>
                </div>

                <div class="p-6 bg-dark-400 rounded-lg mb-4">
                  <div class="text-lg text-gray-200 mb-4">
                    {{ selectedRecipe.steps[currentStep]?.description }}
                  </div>
                  
                  <div class="flex gap-3">
                    <button
                      @click="previousStep"
                      :disabled="currentStep === 0"
                      class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition disabled:opacity-50"
                    >
                      上一步
                    </button>
                    <button
                      @click="nextStep"
                      :disabled="currentStep === selectedRecipe.steps.length - 1"
                      class="flex-1 px-4 py-2 bg-primary-500 text-dark-500 rounded-lg hover:bg-primary-400 transition disabled:opacity-50"
                    >
                      下一步
                    </button>
                  </div>
                </div>

                <!-- AI助手 -->
                <div class="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                  <div class="flex items-start gap-3">
                    <span class="text-2xl">💡</span>
                    <div class="flex-1">
                      <div class="font-medium text-blue-300 mb-1">AI提示</div>
                      <div class="text-sm text-gray-300">
                        {{ getStepTip(currentStep) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 错误诊断模式 -->
          <div v-else-if="selectedMode === 'diagnose'" class="card-dark p-6">
            <h2 class="text-2xl font-bold text-primary-400 mb-6">🔍 烹饪问题诊断</h2>
            
            <div class="space-y-6">
              <!-- 上传图片 -->
              <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">
                  上传菜品图片
                </label>
                <div
                  @click="triggerFileUpload"
                  class="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-primary-500 transition"
                >
                  <div v-if="!diagnosisImage" class="text-gray-400">
                    <div class="text-4xl mb-2">📸</div>
                    <p>点击上传图片</p>
                    <p class="text-xs mt-1">支持 JPG、PNG 格式</p>
                  </div>
                  <div v-else>
                    <img :src="diagnosisImage" alt="诊断图片" class="max-h-64 mx-auto rounded-lg" />
                  </div>
                </div>
                <input
                  ref="diagnosisFileInput"
                  type="file"
                  accept="image/*"
                  @change="handleDiagnosisImage"
                  class="hidden"
                />
              </div>

              <!-- 问题描述 -->
              <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">
                  描述遇到的问题
                </label>
                <textarea
                  v-model="diagnosisProblem"
                  rows="4"
                  placeholder="例如：炒出来的菜太咸了、肉炒不熟、颜色不对等..."
                  class="w-full px-4 py-3 bg-dark-400 border-2 border-gray-600 rounded-lg text-gray-200 placeholder-gray-500 focus:border-primary-500 focus:outline-none"
                ></textarea>
              </div>

              <!-- 诊断按钮 -->
              <button
                @click="diagnoseProblem"
                :disabled="!diagnosisImage || !diagnosisProblem || isDiagnosing"
                class="w-full py-3 px-6 bg-primary-500 text-dark-500 rounded-lg hover:bg-primary-400 transition font-medium disabled:bg-gray-600 disabled:text-gray-400"
              >
                {{ isDiagnosing ? '诊断中...' : '🔍 开始诊断' }}
              </button>

              <!-- 诊断结果 -->
              <div v-if="diagnosisResult" class="p-6 bg-dark-400 rounded-lg">
                <h3 class="text-lg font-bold text-primary-300 mb-3">诊断结果</h3>
                <div class="space-y-3 text-sm text-gray-300 whitespace-pre-wrap">
                  {{ diagnosisResult }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import NavigationBar from '@/components/NavigationBar.vue'
import SkillDetailModal from '@/components/SkillDetailModal.vue'
import { recipeApi } from '@/services/recipeApi'

const router = useRouter()

// 学习模式
const learningModes = [
  { id: 'chat', name: 'AI对话', icon: '🤖', description: '随时问答' },
  { id: 'skills', name: '技巧知识库', icon: '📚', description: '系统学习' },
  { id: 'guide', name: '实时指导', icon: '🎯', description: '分步教学' },
  { id: 'diagnose', name: '问题诊断', icon: '🔍', description: '解决困惑' },
]

const selectedMode = ref('chat')

// 今日技巧
const dailyTips = [
  { title: '炒菜火候', content: '大火快炒保持蔬菜脆嫩，中火慢炖入味' },
  { title: '盐的时机', content: '炒青菜出锅前放盐，避免出水' },
  { title: '刀工技巧', content: '顺纹切肉逆纹切，肉质更嫩' },
]

// AI对话
const chatHistory = ref<Array<{ role: string; content: string; time: string }>>([])
const userInput = ref('')
const isThinking = ref(false)

const quickQuestions = [
  '如何让肉更嫩？',
  '炒菜怎么不粘锅？',
  '如何掌握火候？',
  '调味料的比例？',
]

// 烹饪技巧
const cookingSkills = [
  { id: 1, icon: '🔪', title: '刀工基础', description: '切、片、丝、丁的标准技法', lessons: 8 },
  { id: 2, icon: '🔥', title: '火候掌握', description: '大火、中火、小火的运用', lessons: 6 },
  { id: 3, icon: '🧂', title: '调味技巧', description: '盐、糖、醋、酱油的黄金比例', lessons: 10 },
  { id: 4, icon: '🥘', title: '烹饪方法', description: '炒、煎、炸、蒸、煮、炖', lessons: 12 },
  { id: 5, icon: '🥩', title: '食材处理', description: '肉类、海鲜、蔬菜的预处理', lessons: 9 },
  { id: 6, icon: '🍜', title: '汤品制作', description: '高汤、清汤、浓汤的秘诀', lessons: 7 },
]

// 技巧详情模态框
const showSkillModal = ref(false)
const selectedSkill = ref<any>(null)

// 实时指导
const selectedRecipe = ref<any>(null)
const currentStep = ref(0)

// 错误诊断
const diagnosisFileInput = ref<HTMLInputElement>()
const diagnosisImage = ref('')
const diagnosisProblem = ref('')
const diagnosisResult = ref('')
const isDiagnosing = ref(false)

/**
 * 选择模式
 */
function selectMode(mode: string) {
  selectedMode.value = mode
}

/**
 * 发送消息
 */
async function sendMessage() {
  if (!userInput.value.trim() || isThinking.value) return

  const question = userInput.value.trim()
  const now = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })

  // 添加用户消息
  chatHistory.value.push({
    role: 'user',
    content: question,
    time: now
  })

  userInput.value = ''
  isThinking.value = true

  // 添加一个空的AI消息，用于流式更新
  const aiMessageIndex = chatHistory.value.length
  chatHistory.value.push({
    role: 'assistant',
    content: '',
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  })

  try {
    // 调用AI服务（流式）
    await recipeApi.askCookingQuestion(question, (chunk: string) => {
      // 更新AI消息内容
      chatHistory.value[aiMessageIndex].content += chunk
    })
    
  } catch (error) {
    // 如果出错，显示错误消息
    chatHistory.value[aiMessageIndex].content = '抱歉，我现在有点忙，请稍后再试。'
    console.error('AI对话失败:', error)
  } finally {
    isThinking.value = false
  }
}

/**
 * 快速提问
 */
function askQuickQuestion(question: string) {
  userInput.value = question
  sendMessage()
}

/**
 * 查看技巧详情
 */
function viewSkillDetail(skill: any) {
  selectedSkill.value = skill
  showSkillModal.value = true
}

/**
 * 关闭技巧详情模态框
 */
function closeSkillModal() {
  showSkillModal.value = false
  selectedSkill.value = null
}

/**
 * 上一步
 */
function previousStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

/**
 * 下一步
 */
function nextStep() {
  if (selectedRecipe.value && currentStep.value < selectedRecipe.value.steps.length - 1) {
    currentStep.value++
  }
}

/**
 * 获取步骤提示
 */
function getStepTip(step: number): string {
  const tips = [
    '准备好所有食材，确保新鲜度',
    '注意火候，避免烧焦',
    '适时翻炒，受热均匀',
    '调味要适量，可以尝一下',
    '注意出锅时机，保持最佳口感',
  ]
  return tips[step % tips.length]
}

/**
 * 触发文件上传
 */
function triggerFileUpload() {
  diagnosisFileInput.value?.click()
}

/**
 * 处理诊断图片
 */
function handleDiagnosisImage(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      diagnosisImage.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

/**
 * 诊断问题
 */
async function diagnoseProblem() {
  if (!diagnosisImage.value || !diagnosisProblem.value) return

  isDiagnosing.value = true
  diagnosisResult.value = ''

  try {
    const result = await recipeApi.diagnoseCookingProblem(diagnosisProblem.value)
    diagnosisResult.value = result
  } catch (error) {
    diagnosisResult.value = '诊断失败，请稍后重试'
  } finally {
    isDiagnosing.value = false
  }
}
</script>
