# Frontend App

## 🎨 AI 菜谱平台前端

基于 Vue 3 + TypeScript + Vite 构建的单页应用，负责用户交互、页面编排、菜谱展示、图片上传与烹饪辅助体验。

## ✨ Pages

- `首页`：AI 菜谱生成主流程
- `美食盲盒`：随机菜品选择体验
- `烹饪学堂`：实时问答与问题诊断
- `随料大搜`：按食材搜索 / 推荐 / 解析菜品所需食材
- `历史记录`：查看已保存菜谱
- `菜谱详情`：展示单条菜谱完整信息

## 🛠️ Stack

[![Vue](https://img.shields.io/badge/Vue-3.4-42b883?logo=vue.js&logoColor=white)](../frontend)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178c6?logo=typescript&logoColor=white)](../frontend)
[![Vite](https://img.shields.io/badge/Vite-5.x-646cff?logo=vite&logoColor=white)](../frontend)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06b6d4?logo=tailwindcss&logoColor=white)](../frontend)

- Vue 3
- TypeScript
- Vite
- Vue Router
- Axios
- Tailwind CSS
- Pinia

## 📁 Structure

```text
frontend/
├─ src/
│  ├─ components/        # 通用组件
│  ├─ views/             # 页面级视图
│  ├─ router/            # 路由定义
│  ├─ services/          # API 请求封装
│  ├─ composables/       # 组合式逻辑
│  ├─ types/             # 类型定义
│  ├─ App.vue
│  └─ main.ts
├─ nginx.conf            # 生产反向代理配置
├─ Dockerfile
├─ package.json
└─ README.md
```

## 🚀 Start Development

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Run dev server

```bash
npm run dev
```

默认访问地址：`http://localhost:5173`

### 3. Build for production

```bash
npm run build
```

### 4. Preview production build

```bash
npm run preview
```

## 🧭 Routes

- `/`
- `/blind-box`
- `/cooking-school`
- `/search`
- `/history`
- `/recipe/:id`

## 🔗 API Communication

开发环境下，前端通过配置或代理访问后端。

### 本地开发

- 前端：`http://localhost:5173`
- 后端：`http://localhost:8000`

### Docker / Production

生产环境默认通过 `frontend/nginx.conf` 把以下路径代理到后端：

- `/api/`
- `/uploads/`
- `/health`
- `/docs`
- `/redoc`
- `/openapi.json`

如果根目录 `.env` 中 `VITE_API_BASE_URL` 留空，前端会优先使用同源反向代理。

## 🧩 Key UI Modules

- `RecipeGeneratorForm`：首页主流程表单
- `RecipeDisplay`：菜谱结果展示
- `ImageUploader`：图片上传与识别入口
- `NavigationBar` / `ModernNavigation`：导航系统
- `RecipeHistory`：历史菜谱列表
- `SkillDetailModal`：交互式详情弹窗

## 📌 Notes

- 美食盲盒中的 `效果图功能` 已暂时关闭，页面会展示静态提示，不再触发生成接口。
- 页面已适配 Docker 部署下的 Nginx 反代路径。
- 如需切换接口地址，优先调整根目录 `.env` 中的 `VITE_API_BASE_URL`。

## 🐳 Docker Build

前端容器会在构建阶段注入：

```env
VITE_API_BASE_URL=
```

如果留空，则生产环境通过 Nginx 同源代理调用后端；这也是当前推荐配置。

## 🧪 Common Commands

```bash
npm run dev
npm run build
npm run preview
```

## 📄 Related Docs

- [Root README](../README.md)
- [Backend README](../backend/README.md)
