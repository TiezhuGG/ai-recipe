<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70" @click.self="close">
    <div class="card-dark max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6">
      <!-- 头部 -->
      <div class="flex items-start justify-between mb-6">
        <div class="flex items-center gap-3">
          <span class="text-4xl">{{ skill.icon }}</span>
          <div>
            <h2 class="text-2xl font-bold text-primary-400">{{ skill.title }}</h2>
            <p class="text-sm text-gray-400">{{ skill.lessons }} 个课程</p>
          </div>
        </div>
        <button
          @click="close"
          class="text-gray-400 hover:text-gray-200 transition"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 简介 -->
      <div class="mb-6 p-4 bg-dark-400 rounded-lg">
        <p class="text-gray-300">{{ skill.description }}</p>
      </div>

      <!-- 课程列表 -->
      <div class="space-y-4">
        <h3 class="text-lg font-bold text-gray-200">课程内容</h3>
        <div
          v-for="(lesson, index) in lessons"
          :key="index"
          class="p-4 bg-dark-400 rounded-lg hover:bg-dark-300 cursor-pointer transition"
          @click="selectLesson(index)"
        >
          <div class="flex items-start gap-3">
            <div class="flex-shrink-0 w-8 h-8 bg-primary-500 text-dark-500 rounded-full flex items-center justify-center font-bold">
              {{ index + 1 }}
            </div>
            <div class="flex-1">
              <h4 class="font-medium text-primary-300 mb-1">{{ lesson.title }}</h4>
              <p class="text-sm text-gray-400">{{ lesson.description }}</p>
              <div class="mt-2 flex items-center gap-4 text-xs text-gray-500">
                <span>⏱️ {{ lesson.duration }}</span>
                <span>📊 {{ lesson.difficulty }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 课程详情 -->
      <div v-if="selectedLesson !== null" class="mt-6 p-6 bg-primary-500/10 border-2 border-primary-500 rounded-lg">
        <h3 class="text-xl font-bold text-primary-400 mb-4">{{ lessons[selectedLesson].title }}</h3>
        <div class="space-y-4 text-gray-300">
          <div v-for="(content, idx) in lessons[selectedLesson].content" :key="idx">
            <h4 class="font-medium text-primary-300 mb-2">{{ content.subtitle }}</h4>
            <p class="text-sm whitespace-pre-line">{{ content.text }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  show: boolean
  skill: any
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'close': []
}>()

const selectedLesson = ref<number | null>(null)

// 根据技能ID生成课程内容
const lessons = computed(() => {
  return getSkillLessons(props.skill.id)
})

function close() {
  selectedLesson.value = null
  emit('close')
}

function selectLesson(index: number) {
  selectedLesson.value = index
}

function getSkillLessons(skillId: number) {
  const lessonsMap: Record<number, any[]> = {
    1: [ // 刀工基础
      {
        title: '持刀姿势与安全',
        description: '正确的持刀方法和安全注意事项',
        duration: '10分钟',
        difficulty: '入门',
        content: [
          {
            subtitle: '正确持刀',
            text: '1. 握刀柄，食指和拇指捏住刀身根部\n2. 其余三指自然握住刀柄\n3. 刀刃与砧板保持垂直\n4. 手腕放松，用手臂力量切菜'
          },
          {
            subtitle: '安全要点',
            text: '1. 切菜时手指弯曲，指关节顶住刀面\n2. 刀具要锋利，钝刀更危险\n3. 切菜时注意力集中\n4. 刀具用完立即清洗收好'
          }
        ]
      },
      {
        title: '切片技法',
        description: '如何切出均匀的薄片',
        duration: '15分钟',
        difficulty: '入门',
        content: [
          {
            subtitle: '基本要领',
            text: '1. 食材放稳，必要时切一刀垫底\n2. 刀刃与砧板垂直\n3. 每刀厚度一致\n4. 切片时推拉结合'
          },
          {
            subtitle: '常见应用',
            text: '土豆片、黄瓜片、肉片等\n厚度：2-3mm为宜'
          }
        ]
      },
      {
        title: '切丝技法',
        description: '将食材切成细丝的方法',
        duration: '20分钟',
        difficulty: '进阶',
        content: [
          {
            subtitle: '操作步骤',
            text: '1. 先将食材切成薄片\n2. 将薄片叠放整齐\n3. 切成细丝，粗细一致\n4. 丝的粗细：2-3mm'
          }
        ]
      },
      {
        title: '切丁技法',
        description: '切出大小均匀的丁块',
        duration: '15分钟',
        difficulty: '入门',
        content: [
          {
            subtitle: '切丁步骤',
            text: '1. 先切片\n2. 再切条\n3. 最后切丁\n4. 大小：0.5-1cm见方'
          }
        ]
      },
      {
        title: '切块技法',
        description: '大块食材的切法',
        duration: '10分钟',
        difficulty: '入门',
        content: [
          {
            subtitle: '切块要点',
            text: '1. 根据烹饪需要确定大小\n2. 块状要均匀\n3. 炖煮用大块（3-4cm）\n4. 快炒用小块（1-2cm）'
          }
        ]
      },
      {
        title: '剁碎技法',
        description: '将食材剁成碎末',
        duration: '12分钟',
        difficulty: '入门',
        content: [
          {
            subtitle: '剁碎方法',
            text: '1. 先粗切成小块\n2. 双手持刀交替剁\n3. 边剁边聚拢\n4. 剁至所需细度'
          }
        ]
      },
      {
        title: '滚刀块技法',
        description: '适合炖煮的不规则块状',
        duration: '15分钟',
        difficulty: '进阶',
        content: [
          {
            subtitle: '滚刀要领',
            text: '1. 斜刀切一刀\n2. 食材滚动90度\n3. 再斜刀切一刀\n4. 重复至切完\n5. 适合：萝卜、土豆等'
          }
        ]
      },
      {
        title: '花刀技法',
        description: '装饰性刀工技巧',
        duration: '25分钟',
        difficulty: '高级',
        content: [
          {
            subtitle: '常见花刀',
            text: '1. 十字花刀：在食材表面切十字纹\n2. 麦穗花刀：斜切平行线\n3. 菊花刀：放射状切纹\n4. 用于：鱿鱼、腰花等'
          }
        ]
      }
    ],
    2: [ // 火候掌握
      {
        title: '认识火候',
        description: '了解大火、中火、小火的区别',
        duration: '10分钟',
        difficulty: '入门',
        content: [
          {
            subtitle: '火候分类',
            text: '大火（旺火）：火焰高，温度高，适合快炒\n中火：火焰中等，温度适中，适合煎炸\n小火（文火）：火焰小，温度低，适合炖煮'
          }
        ]
      },
      {
        title: '大火快炒',
        description: '保持食材脆嫩的秘诀',
        duration: '15分钟',
        difficulty: '入门',
        content: [
          {
            subtitle: '大火要点',
            text: '1. 锅要烧热\n2. 油温要高（7-8成热）\n3. 快速翻炒\n4. 时间短（2-3分钟）\n5. 适合：青菜、肉片'
          }
        ]
      },
      {
        title: '中火煎炸',
        description: '外酥里嫩的关键',
        duration: '20分钟',
        difficulty: '进阶',
        content: [
          {
            subtitle: '煎炸技巧',
            text: '1. 油温5-6成热\n2. 食材下锅后不要频繁翻动\n3. 一面金黄再翻面\n4. 保持中火，避免外焦里生'
          }
        ]
      },
      {
        title: '小火慢炖',
        description: '入味软烂的秘密',
        duration: '15分钟',
        difficulty: '入门',
        content: [
          {
            subtitle: '炖煮要领',
            text: '1. 小火慢炖，保持微沸\n2. 时间充足（1-2小时）\n3. 中途不要频繁开盖\n4. 适合：炖肉、煲汤'
          }
        ]
      },
      {
        title: '油温判断',
        description: '如何判断油温是否合适',
        duration: '12分钟',
        difficulty: '进阶',
        content: [
          {
            subtitle: '油温判断法',
            text: '3-4成热：油面平静，无烟\n5-6成热：油面波动，微烟\n7-8成热：油面翻动，有烟\n9-10成热：大量冒烟（过热）'
          }
        ]
      },
      {
        title: '火候转换',
        description: '烹饪过程中的火候调整',
        duration: '18分钟',
        difficulty: '高级',
        content: [
          {
            subtitle: '转换技巧',
            text: '1. 大火烧开，小火慢炖\n2. 中火煎至金黄，小火焖熟\n3. 大火收汁，快速翻炒\n4. 根据食材状态灵活调整'
          }
        ]
      }
    ],
    3: [ // 调味技巧
      {
        title: '基础调味料认识',
        description: '常用调味料的特点和用法',
        duration: '15分钟',
        difficulty: '入门',
        content: [
          {
            subtitle: '基本调味料',
            text: '盐：提鲜、定味\n糖：提鲜、去腥\n醋：解腻、增香\n酱油：上色、增鲜\n料酒：去腥、增香'
          }
        ]
      },
      {
        title: '黄金调味比例',
        description: '常用调味料的配比',
        duration: '20分钟',
        difficulty: '进阶',
        content: [
          {
            subtitle: '基础比例',
            text: '糖醋汁：糖2：醋1：酱油0.5\n红烧汁：酱油2：糖1：料酒1\n蒜蓉汁：蒜末：油：盐 = 3:2:1'
          }
        ]
      },
      {
        title: '调味时机',
        description: '什么时候放调料最合适',
        duration: '18分钟',
        difficulty: '进阶',
        content: [
          {
            subtitle: '放盐时机',
            text: '炒青菜：出锅前放盐\n炖肉：中途放盐\n凉拌：拌好后立即放盐'
          },
          {
            subtitle: '其他调料',
            text: '料酒：食材下锅后立即放\n醋：出锅前放，保持香味\n味精：关火后放，避免高温破坏'
          }
        ]
      },
      {
        title: '复合调味',
        description: '多种调料的搭配使用',
        duration: '25分钟',
        difficulty: '高级',
        content: [
          {
            subtitle: '调味原则',
            text: '1. 咸鲜为主，酸甜为辅\n2. 一菜一味，突出主味\n3. 调料要适量，可以后补\n4. 注意调料之间的相互作用'
          }
        ]
      }
    ],
    4: [ // 烹饪方法
      {
        title: '炒的技法',
        description: '最常用的烹饪方法',
        duration: '20分钟',
        difficulty: '入门',
        content: [
          {
            subtitle: '炒菜要点',
            text: '1. 热锅凉油或热锅热油\n2. 大火快炒\n3. 不断翻动\n4. 时间短，保持脆嫩'
          }
        ]
      },
      {
        title: '煎的技法',
        description: '形成金黄外皮的方法',
        duration: '18分钟',
        difficulty: '入门',
        content: [
          {
            subtitle: '煎的要领',
            text: '1. 中火，油温适中\n2. 食材下锅后不要急于翻动\n3. 一面金黄再翻面\n4. 保持火候稳定'
          }
        ]
      },
      {
        title: '炸的技法',
        description: '外酥里嫩的油炸技巧',
        duration: '25分钟',
        difficulty: '进阶',
        content: [
          {
            subtitle: '油炸要点',
            text: '1. 油量要足够\n2. 油温要合适（5-7成热）\n3. 分批下锅，避免温度骤降\n4. 炸至金黄捞出\n5. 复炸可以更酥脆'
          }
        ]
      },
      {
        title: '蒸的技法',
        description: '保持食材原味的健康烹饪',
        duration: '15分钟',
        difficulty: '入门',
        content: [
          {
            subtitle: '蒸的要领',
            text: '1. 水要烧开后再放食材\n2. 保持大火，蒸汽充足\n3. 时间要准确\n4. 蒸好后立即取出'
          }
        ]
      },
      {
        title: '煮的技法',
        description: '水煮类菜肴的制作',
        duration: '15分钟',
        difficulty: '入门',
        content: [
          {
            subtitle: '煮的方法',
            text: '1. 冷水下锅：肉类、骨头\n2. 开水下锅：蔬菜、面条\n3. 保持适当火候\n4. 注意煮的时间'
          }
        ]
      },
      {
        title: '炖的技法',
        description: '软烂入味的炖煮方法',
        duration: '20分钟',
        difficulty: '进阶',
        content: [
          {
            subtitle: '炖的要领',
            text: '1. 先大火烧开\n2. 转小火慢炖\n3. 时间要充足（1-2小时）\n4. 中途少开盖\n5. 汤汁浓郁，食材软烂'
          }
        ]
      }
    ],
    5: [ // 食材处理
      {
        title: '肉类处理',
        description: '让肉更嫩的秘诀',
        duration: '20分钟',
        difficulty: '进阶',
        content: [
          {
            subtitle: '嫩肉方法',
            text: '1. 逆纹切肉\n2. 用淀粉、蛋清腌制\n3. 加少许油拌匀\n4. 腌制15-30分钟\n5. 快速滑炒'
          },
          {
            subtitle: '去腥方法',
            text: '1. 用料酒腌制\n2. 加姜片、葱段\n3. 焯水去血沫\n4. 加醋或柠檬汁'
          }
        ]
      },
      {
        title: '海鲜处理',
        description: '保持海鲜鲜嫩的技巧',
        duration: '18分钟',
        difficulty: '进阶',
        content: [
          {
            subtitle: '海鲜处理要点',
            text: '1. 新鲜最重要\n2. 清洗干净\n3. 去除内脏和腥线\n4. 用料酒、姜去腥\n5. 烹饪时间要短'
          }
        ]
      },
      {
        title: '蔬菜处理',
        description: '保持蔬菜营养和口感',
        duration: '15分钟',
        difficulty: '入门',
        content: [
          {
            subtitle: '蔬菜处理',
            text: '1. 先洗后切\n2. 切好后尽快烹饪\n3. 焯水时加盐和油\n4. 快速过凉水保持翠绿\n5. 大火快炒'
          }
        ]
      }
    ],
    6: [ // 汤品制作
      {
        title: '高汤制作',
        description: '鲜美高汤的熬制方法',
        duration: '30分钟',
        difficulty: '进阶',
        content: [
          {
            subtitle: '高汤要领',
            text: '1. 选用骨头、鸡架等\n2. 冷水下锅，慢慢加热\n3. 撇去浮沫\n4. 小火慢熬2-3小时\n5. 不要加盐，保持原味'
          }
        ]
      },
      {
        title: '清汤制作',
        description: '清澈鲜美的清汤技巧',
        duration: '25分钟',
        difficulty: '进阶',
        content: [
          {
            subtitle: '清汤要点',
            text: '1. 食材要新鲜\n2. 水要一次加足\n3. 保持小火，不要沸腾\n4. 及时撇去浮沫\n5. 汤色清澈透明'
          }
        ]
      },
      {
        title: '浓汤制作',
        description: '浓郁奶白汤的秘密',
        duration: '28分钟',
        difficulty: '高级',
        content: [
          {
            subtitle: '奶白汤技巧',
            text: '1. 先煎后煮\n2. 大火滚煮\n3. 加入足够的脂肪（油、骨髓）\n4. 持续沸腾\n5. 汤色奶白浓郁'
          }
        ]
      }
    ]
  }

  return lessonsMap[skillId] || []
}
</script>
