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
            
            <!-- 选择菜谱 -->
            <div v-if="!selectedRecipe" class="space-y-6">
              <div class="text-center py-8">
                <div class="text-5xl mb-4">🍳</div>
                <p class="text-gray-400 mb-6">选择一个历史菜谱开始实时指导</p>
              </div>

              <!-- 历史菜谱列表 -->
              <div v-if="guideRecipes.length > 0" class="space-y-3">
                <h3 class="text-lg font-bold text-gray-300 mb-3">我的菜谱</h3>
                <div class="grid md:grid-cols-2 gap-3">
                  <div
                    v-for="recipe in guideRecipes"
                    :key="recipe.id"
                    @click="startGuide(recipe)"
                    class="p-4 bg-gray-700 rounded-lg hover:bg-gray-600 cursor-pointer transition border border-gray-600 hover:border-primary-500"
                  >
                    <div class="flex items-center gap-3">
                      <div class="text-3xl">👨‍🍳</div>
                      <div class="flex-1">
                        <div class="font-bold text-primary-300">{{ recipe.name }}</div>
                        <div class="text-xs text-gray-400 mt-1">
                          {{ recipe.steps?.length || 0 }} 个步骤 · {{ recipe.cookingTime }}分钟
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 空状态 -->
              <div v-else class="text-center py-8">
                <p class="text-gray-500 mb-4">还没有保存的菜谱</p>
                <button
                  @click="$router.push('/')"
                  class="px-6 py-3 bg-primary-500 text-gray-900 rounded-lg hover:bg-primary-400 transition font-medium"
                >
                  去生成菜谱
                </button>
              </div>
            </div>

            <!-- 烹饪指导界面 -->
            <div v-else class="space-y-6">
              <!-- 菜谱信息 -->
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-xl font-bold text-gray-200">{{ selectedRecipe.name }}</h3>
                  <div class="text-sm text-gray-400 mt-1">
                    难度：{{ getDifficultyText(selectedRecipe.difficulty) }} · 
                    预计时间：{{ selectedRecipe.cookingTime }}分钟
                  </div>
                </div>
                <button
                  @click="exitGuide"
                  class="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition text-sm"
                >
                  退出指导
                </button>
              </div>

              <!-- 进度条 -->
              <div class="space-y-2">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-gray-400">烹饪进度</span>
                  <span class="text-primary-400 font-medium">
                    {{ currentStep + 1 }} / {{ selectedRecipe.steps?.length || 0 }}
                  </span>
                </div>
                <div class="w-full bg-gray-700 rounded-full h-2">
                  <div
                    class="bg-primary-500 h-2 rounded-full transition-all duration-300"
                    :style="{ width: `${((currentStep + 1) / (selectedRecipe.steps?.length || 1)) * 100}%` }"
                  ></div>
                </div>
              </div>

              <!-- 当前步骤 -->
              <div class="p-6 bg-gradient-to-br from-primary-500/10 to-blue-500/10 border-2 border-primary-500/30 rounded-lg">
                <div class="flex items-start gap-4 mb-4">
                  <div class="text-4xl">{{ getStepIcon(currentStep) }}</div>
                  <div class="flex-1">
                    <div class="text-sm text-primary-400 font-medium mb-2">
                      步骤 {{ currentStep + 1 }}
                    </div>
                    <div class="text-lg text-gray-200 leading-relaxed">
                      {{ selectedRecipe.steps?.[currentStep]?.description || '步骤信息不可用' }}
                    </div>
                  </div>
                </div>

                <!-- 计时器 -->
                <div v-if="stepTimer > 0" class="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg">
                  <span class="text-2xl">⏱️</span>
                  <div class="flex-1">
                    <div class="text-sm text-gray-400">建议时间</div>
                    <div class="text-xl font-bold text-primary-400">
                      {{ formatTime(stepTimer) }}
                    </div>
                  </div>
                  <button
                    v-if="!isTimerRunning"
                    @click="startTimer"
                    class="px-4 py-2 bg-primary-500 text-gray-900 rounded-lg hover:bg-primary-400 transition text-sm font-medium"
                  >
                    开始计时
                  </button>
                  <button
                    v-else
                    @click="stopTimer"
                    class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-400 transition text-sm font-medium"
                  >
                    停止
                  </button>
                </div>
              </div>

              <!-- AI提示 -->
              <div class="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                <div class="flex items-start gap-3">
                  <span class="text-2xl">💡</span>
                  <div class="flex-1">
                    <div class="font-medium text-blue-300 mb-1">AI小贴士</div>
                    <div class="text-sm text-gray-300">
                      {{ getStepTip(currentStep) }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- 快速提问 -->
              <div class="p-4 bg-gray-700 rounded-lg">
                <div class="text-sm text-gray-400 mb-3 flex items-center gap-2">
                  <span class="text-lg">💡</span>
                  <span>遇到问题？快速提问：</span>
                </div>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="question in guideQuickQuestions"
                    :key="question"
                    @click="askGuideQuestion(question)"
                    :disabled="isLoadingGuideAnswer"
                    :class="[
                      'question-button px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 transform',
                      isLoadingGuideAnswer 
                        ? 'bg-gray-600 text-gray-500 cursor-not-allowed' 
                        : 'bg-gray-600 text-gray-300 hover:bg-primary-500 hover:text-white hover:scale-105 hover:shadow-lg active:scale-95'
                    ]"
                  >
                    <span v-if="isLoadingGuideAnswer && guideQuestion === question" class="inline-flex items-center gap-2">
                      <div class="w-3 h-3 border border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                      {{ question }}
                    </span>
                    <span v-else>{{ question }}</span>
                  </button>
                </div>
                
                <!-- 提示信息 -->
                <div v-if="!isLoadingGuideAnswer" class="mt-3 text-xs text-gray-500 flex items-center gap-1">
                  <span>💬</span>
                  <span>点击问题获得针对当前步骤的专业指导</span>
                </div>
                <div v-else class="mt-3 text-xs text-blue-400 flex items-center gap-1">
                  <span>🤖</span>
                  <span>AI正在为您分析当前烹饪步骤...</span>
                </div>
              </div>

              <!-- AI回答区域 -->
              <div v-if="guideAnswer || isLoadingGuideAnswer" class="p-6 bg-gradient-to-br from-blue-500/10 to-purple-500/10 border-2 border-blue-500/30 rounded-lg">
                <div class="flex items-start gap-4 mb-4">
                  <div class="relative">
                    <span class="text-3xl">🤖</span>
                    <!-- AI思考动画 -->
                    <div v-if="isLoadingGuideAnswer" class="absolute -top-1 -right-1 w-4 h-4 bg-blue-400 rounded-full animate-pulse"></div>
                  </div>
                  <div class="flex-1">
                    <div class="font-medium text-blue-300 mb-2">AI烹饪助手</div>
                    <div class="text-sm text-gray-400 mb-3 italic">{{ guideQuestion }}</div>
                  </div>
                  <button
                    v-if="!isLoadingGuideAnswer"
                    @click="clearGuideAnswer"
                    class="text-gray-500 hover:text-gray-300 transition-colors duration-200 text-xl"
                    title="关闭回答"
                  >
                    ×
                  </button>
                </div>

                <!-- 加载状态 - 漂亮的动画 -->
                <div v-if="isLoadingGuideAnswer" class="space-y-4">
                  <!-- 思考动画 -->
                  <div class="flex items-center gap-3 p-4 bg-blue-500/5 rounded-lg loading-breathe">
                    <div class="flex gap-1">
                      <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                      <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                      <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                    </div>
                    <span class="text-blue-300 font-medium">AI正在分析您的问题...</span>
                  </div>

                  <!-- 进度条动画 -->
                  <div class="space-y-2">
                    <div class="flex justify-between text-xs text-gray-400">
                      <span>分析烹饪步骤</span>
                      <span>生成专业建议</span>
                    </div>
                    <div class="w-full bg-gray-700 rounded-full h-1.5 overflow-hidden">
                      <div class="h-full bg-gradient-to-r from-blue-400 to-purple-400 rounded-full animate-shimmer"></div>
                    </div>
                  </div>

                  <!-- 提示文字 -->
                  <div class="text-center ai-thinking">
                    <div class="text-sm text-gray-400 mb-2">🧠 AI大厨正在思考...</div>
                    <div class="text-xs text-gray-500">基于当前步骤为您提供专业指导</div>
                  </div>
                </div>

                <!-- AI回答内容 -->
                <div v-else-if="guideAnswer" class="space-y-3">
                  <!-- 回答内容 -->
                  <div class="p-4 bg-gray-800/50 rounded-lg border-l-4 border-blue-400">
                    <div class="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">{{ guideAnswer }}</div>
                  </div>
                  
                  <!-- 底部操作 -->
                  <div class="flex items-center justify-between pt-2">
                    <div class="flex items-center gap-2 text-xs text-gray-500">
                      <span class="w-2 h-2 bg-green-400 rounded-full"></span>
                      <span>回答完成</span>
                    </div>
                    <div class="flex gap-2">
                      <button
                        @click="askGuideQuestion(guideQuestion)"
                        class="px-3 py-1 text-xs bg-blue-500/20 text-blue-300 rounded-full hover:bg-blue-500/30 transition-colors duration-200"
                        title="重新提问"
                      >
                        🔄 重新提问
                      </button>
                      <button
                        @click="clearGuideAnswer"
                        class="px-3 py-1 text-xs bg-gray-600 text-gray-300 rounded-full hover:bg-gray-500 transition-colors duration-200"
                      >
                        关闭
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 导航按钮 -->
              <div class="flex gap-3">
                <button
                  @click="previousStep"
                  :disabled="currentStep === 0"
                  class="px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  ← 上一步
                </button>
                <button
                  v-if="currentStep < (selectedRecipe.steps?.length || 0) - 1"
                  @click="nextStep"
                  class="flex-1 px-6 py-3 bg-primary-500 text-gray-900 rounded-lg hover:bg-primary-400 transition font-medium"
                >
                  下一步 →
                </button>
                <button
                  v-else
                  @click="completeGuide"
                  class="flex-1 px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-400 transition font-medium"
                >
                  🎉 完成烹饪
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import NavigationBar from '@/components/NavigationBar.vue'
import SkillDetailModal from '@/components/SkillDetailModal.vue'
import { recipeApi } from '@/services/recipeApi'

// 学习模式
const learningModes = [
  { id: 'chat', name: 'AI对话', icon: '🤖', description: '随时问答' },
  { id: 'skills', name: '技巧知识库', icon: '📚', description: '系统学习' },
  { id: 'guide', name: '实时指导', icon: '🎯', description: '分步教学' },
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
  '炒菜时总是粘锅怎么办？',
  '怎么判断肉是否炒熟了？',
  '为什么我做的汤总是很淡？',
  '如何让炒出来的青菜保持翠绿？',
  '炒蛋怎么做得更嫩滑？',
  '为什么我炒的菜总是出水？',
  '怎么让米饭更香更好吃？',
  '如何去除肉类的腥味？',
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
const guideRecipes = ref<any[]>([])
const stepTimer = ref(0)
const isTimerRunning = ref(false)
const timerInterval = ref<any>(null)

// 实时指导快速提问
const guideQuestion = ref('')
const guideAnswer = ref('')
const isLoadingGuideAnswer = ref(false)

// 实时指导专用的快速问题
const guideQuickQuestions = [
  '这一步需要多长时间？',
  '火候应该怎么控制？',
  '如何判断是否做好了？',
  '可以用什么替代食材？',
  '这一步的关键点是什么？',
  '出现问题怎么补救？'
]

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

// 加载历史菜谱用于指导
async function loadGuideRecipes() {
  try {
    const response = await recipeApi.getRecipeHistory(20, 0)
    
    // 获取每个菜谱的完整详情（包含steps）
    const recipesWithDetails = await Promise.all(
      response.recipes.map(async (recipe) => {
        try {
          const fullRecipe = await recipeApi.getRecipeById(recipe.id)
          return fullRecipe
        } catch (error) {
          console.error(`获取菜谱详情失败: ${recipe.id}`, error)
          // 如果获取详情失败，返回基本信息但添加空的steps
          return {
            ...recipe,
            steps: [],
            ingredients: {},
            safetyTips: null
          }
        }
      })
    )
    
    // 只保留有步骤的菜谱
    guideRecipes.value = recipesWithDetails.filter(recipe => 
      recipe.steps && Array.isArray(recipe.steps) && recipe.steps.length > 0
    )
  } catch (error) {
    console.error('加载菜谱失败:', error)
    guideRecipes.value = []
  }
}

// 开始指导
function startGuide(recipe: any) {
  // 确保菜谱有有效的步骤
  if (!recipe.steps || !Array.isArray(recipe.steps) || recipe.steps.length === 0) {
    alert('该菜谱没有详细步骤，无法进行指导')
    return
  }
  
  selectedRecipe.value = recipe
  currentStep.value = 0
  stepTimer.value = getStepTime(0)
}

// 退出指导
function exitGuide() {
  selectedRecipe.value = null
  currentStep.value = 0
  stopTimer()
  clearGuideAnswer()
}

// 获取步骤建议时间（分钟）
function getStepTime(stepIndex: number): number {
  const stepTimes = [5, 3, 8, 5, 2, 10, 3] // 示例时间
  return stepTimes[stepIndex % stepTimes.length] || 5
}

// 格式化时间显示
function formatTime(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} 分钟`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}小时${mins}分钟`
}

// 开始计时
function startTimer() {
  if (isTimerRunning.value) return
  
  isTimerRunning.value = true
  let remainingTime = stepTimer.value * 60 // 转换为秒
  
  timerInterval.value = setInterval(() => {
    remainingTime--
    stepTimer.value = Math.ceil(remainingTime / 60)
    
    if (remainingTime <= 0) {
      stopTimer()
      // 可以添加提醒音效或通知
      alert('⏰ 时间到！请检查当前步骤是否完成。')
    }
  }, 1000)
}

// 停止计时
function stopTimer() {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
  isTimerRunning.value = false
}

// 获取步骤图标
function getStepIcon(stepIndex: number): string {
  const icons = ['🥘', '🔪', '🔥', '🧂', '⏰', '🍳', '✨']
  return icons[stepIndex % icons.length]
}

// 获取难度文本
function getDifficultyText(difficulty: string): string {
  const difficultyMap: Record<string, string> = {
    'easy': '简单',
    'medium': '中等', 
    'hard': '困难'
  }
  return difficultyMap[difficulty] || difficulty
}

// 完成指导
function completeGuide() {
  stopTimer()
  alert('🎉 恭喜！您已完成这道菜的制作！')
  exitGuide()
}

// 上一步
function previousStep() {
  if (currentStep.value > 0) {
    stopTimer()
    currentStep.value--
    stepTimer.value = getStepTime(currentStep.value)
  }
}

// 下一步
function nextStep() {
  if (selectedRecipe.value && selectedRecipe.value.steps && currentStep.value < selectedRecipe.value.steps.length - 1) {
    stopTimer()
    currentStep.value++
    stepTimer.value = getStepTime(currentStep.value)
  }
}

/**
 * 实时指导快速提问
 */
async function askGuideQuestion(question: string) {
  if (!selectedRecipe.value) return
  
  guideQuestion.value = question
  guideAnswer.value = ''
  isLoadingGuideAnswer.value = true
  
  try {
    // 构建包含当前步骤信息的完整问题
    const currentStepInfo = selectedRecipe.value.steps?.[currentStep.value]
    const contextualQuestion = `我正在做"${selectedRecipe.value.name}"，当前在第${currentStep.value + 1}步："${currentStepInfo?.description || '未知步骤'}"。${question}`
    
    // 调用AI服务获取回答
    const answer = await recipeApi.diagnoseCookingProblem(contextualQuestion)
    guideAnswer.value = answer
  } catch (error) {
    console.error('获取AI回答失败:', error)
    guideAnswer.value = '抱歉，AI助手暂时无法回答，请稍后重试。'
  } finally {
    isLoadingGuideAnswer.value = false
  }
}

/**
 * 清空指导回答
 */
function clearGuideAnswer() {
  guideQuestion.value = ''
  guideAnswer.value = ''
}

// 初始化时加载菜谱
onMounted(() => {
  loadGuideRecipes()
})
</script>

<style scoped>
/* 自定义动画 */
@keyframes shimmer {
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 5px rgba(59, 130, 246, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.6);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-3px);
  }
}

/* 加载进度条动画 */
.animate-shimmer {
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.4), transparent);
  background-size: 200px 100%;
  animation: shimmer 1.5s infinite;
}

/* AI思考动画增强 */
.ai-thinking {
  animation: pulse-glow 2s infinite, float 3s ease-in-out infinite;
}

/* 按钮悬停效果 */
.question-button {
  position: relative;
  overflow: hidden;
}

.question-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(34, 197, 94, 0.2), transparent);
  transition: left 0.5s;
}

.question-button:hover::before {
  left: 100%;
}

/* 回答区域入场动画 */
.answer-enter-active {
  animation: slideInUp 0.5s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 加载状态的呼吸效果 */
.loading-breathe {
  animation: breathe 2s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.05);
    opacity: 1;
  }
}
</style>
