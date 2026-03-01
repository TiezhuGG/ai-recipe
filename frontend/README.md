# AI智能菜谱生成平台 - 前端

基于Vue3 + TypeScript + Vite + TailwindCSS的前端应用。

## 技术栈

- Vue 3.4+ (组合式API)
- TypeScript 5.3+
- Vite 5.0+ (构建工具)
- Vue Router 4.2+ (路由管理)
- Pinia 2.1+ (状态管理)
- Axios (HTTP客户端)
- TailwindCSS 3.4+ (CSS框架)

## 项目结构

```
frontend/
├── src/
│   ├── components/     # Vue组件
│   ├── views/          # 页面组件
│   ├── router/         # 路由配置
│   ├── services/       # API服务
│   ├── types/          # TypeScript类型
│   ├── composables/    # 组合式函数
│   ├── App.vue         # 根组件
│   ├── main.ts         # 应用入口
│   └── style.css       # 全局样式
├── public/             # 静态资源
├── index.html          # HTML模板
├── vite.config.ts      # Vite配置
├── tailwind.config.js  # TailwindCSS配置
├── tsconfig.json       # TypeScript配置
└── package.json        # 依赖配置
```

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:5173 启动。

### 3. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

### 4. 预览生产构建

```bash
npm run preview
```

## 开发说明

### 路由

- `/` - 主页（菜谱生成）
- `/history` - 历史记录
- `/recipe/:id` - 菜谱详情

### API代理

开发环境下，Vite会自动代理API请求到后端服务器：

- `/api/*` → `http://localhost:8000/api/*`
- `/uploads/*` → `http://localhost:8000/uploads/*`

### 组件开发

所有组件使用Vue3组合式API（`<script setup>`）和TypeScript。

示例：

```vue
<template>
  <div class="my-component">
    <h1>{{ title }}</h1>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const title = ref('Hello World')
</script>

<style scoped>
.my-component {
  /* 样式 */
}
</style>
```

### 样式

使用TailwindCSS工具类进行样式开发。

常用类：
- 布局: `flex`, `grid`, `container`
- 间距: `p-4`, `m-2`, `space-x-4`
- 颜色: `bg-white`, `text-gray-600`
- 响应式: `md:flex`, `lg:grid-cols-3`

## 待实现功能

- [ ] 食材输入组件
- [ ] 口味和菜系选择器
- [ ] 图片上传组件
- [ ] 特殊人群选择器
- [ ] 菜谱展示组件
- [ ] 历史记录组件
- [ ] API客户端服务
- [ ] 状态管理
- [ ] 响应式设计

## 注意事项

1. 确保后端服务在 http://localhost:8000 运行
2. 使用组合式API和TypeScript
3. 遵循Vue3最佳实践
4. 使用TailwindCSS进行样式开发
5. 确保响应式设计（移动端、平板、桌面）

## 下一步

继续实现任务10-20的前端组件和功能。
