# AI智能菜谱生成平台 - 快速启动指南

## 项目概述

这是一个基于 AI 的智能菜谱生成平台，用户可以通过输入食材、选择口味和菜系，或上传食材图片，快速生成个性化的菜谱。

## 技术栈

### 后端
- Python 3.8+
- FastAPI
- SQLAlchemy
- SQLite (开发) / PostgreSQL (生产)
- 豆包 AI API

### 前端
- Vue 3
- TypeScript
- Vite
- TailwindCSS
- Vue Router
- Axios

## 前置要求

1. Python 3.8 或更高版本
2. Node.js 16 或更高版本
3. 豆包 AI API 密钥

## 安装步骤

### 1. 克隆项目（如果适用）

```bash
# 如果从 git 仓库克隆
git clone <repository-url>
cd <project-directory>
```

### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 复制 .env.example 到 .env
cp .env.example .env

# 编辑 .env 文件，填入你的豆包 API 密钥
# DOUBAO_API_KEY=your_api_key_here
# DOUBAO_API_URL=https://ark.cn-beijing.volces.com/api/v3
```

### 3. 前端设置

```bash
# 打开新终端，进入前端目录
cd frontend

# 安装依赖
npm install
```

## 启动应用

### 1. 启动后端服务

```bash
# 在 backend 目录下
cd backend

# 确保虚拟环境已激活
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 启动服务
python main.py
```

后端服务将在 http://localhost:8000 启动

### 2. 启动前端服务

```bash
# 在新终端，进入 frontend 目录
cd frontend

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

## 访问应用

打开浏览器访问: http://localhost:5173

## 功能测试

### 1. 生成菜谱
1. 在主页输入食材（例如：土豆,番茄,鸡蛋）
2. 选择口味和菜系（可选）
3. 选择特殊人群（可选）
4. 点击"生成菜谱"按钮
5. 查看生成的菜谱

### 2. 图片识别
1. 点击"上传食材图片"区域
2. 选择一张食材图片
3. 等待识别完成
4. 识别的食材会自动添加到食材列表

### 3. 保存菜谱
1. 生成菜谱后，点击"保存菜谱"按钮
2. 菜谱将保存到数据库

### 4. 查看历史
1. 点击导航栏的"历史记录"
2. 查看已保存的菜谱列表
3. 点击任意菜谱查看详情

## 项目结构

```
.
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── repositories/   # 数据访问层
│   │   ├── routers/        # API 路由
│   │   ├── schemas/        # Pydantic 模型
│   │   └── services/       # 业务逻辑
│   ├── main.py             # 应用入口
│   ├── requirements.txt    # Python 依赖
│   └── .env                # 环境变量
│
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/    # Vue 组件
│   │   ├── views/         # 页面视图
│   │   ├── services/      # API 服务
│   │   ├── types/         # TypeScript 类型
│   │   ├── composables/   # 可复用逻辑
│   │   └── router/        # 路由配置
│   ├── package.json       # Node 依赖
│   └── vite.config.ts     # Vite 配置
│
└── .kiro/                 # 项目规范文档
    └── specs/
        └── ai-recipe-generator/
            ├── requirements.md  # 需求文档
            ├── design.md        # 设计文档
            └── tasks.md         # 任务列表
```

## 常见问题

### 1. 后端启动失败
- 检查 Python 版本是否 >= 3.8
- 确保虚拟环境已激活
- 检查 .env 文件是否正确配置
- 确保所有依赖已安装

### 2. 前端启动失败
- 检查 Node.js 版本是否 >= 16
- 删除 node_modules 和 package-lock.json，重新安装
- 检查端口 5173 是否被占用

### 3. API 调用失败
- 确保后端服务正在运行
- 检查豆包 API 密钥是否正确
- 查看浏览器控制台和后端日志

### 4. 图片上传失败
- 检查图片格式（仅支持 JPEG/PNG/WebP）
- 检查图片大小（必须 < 10MB）
- 确保 backend/uploads 目录存在且有写权限

## 开发工具

### 推荐的 IDE
- VS Code
- PyCharm (后端)
- WebStorm (前端)

### 推荐的 VS Code 插件
- Vue Language Features (Volar)
- TypeScript Vue Plugin (Volar)
- Python
- Pylance
- Tailwind CSS IntelliSense

## 测试

### 后端测试
```bash
cd backend
python test_api.py
```

### 前端测试
前端目前没有自动化测试，请参考 `frontend/FRONTEND_VERIFICATION.md` 进行手动测试。

## 部署

部署说明请参考:
- 后端: `backend/README.md`
- 前端: `frontend/README.md`

## 文档

- 需求文档: `.kiro/specs/ai-recipe-generator/requirements.md`
- 设计文档: `.kiro/specs/ai-recipe-generator/design.md`
- 任务列表: `.kiro/specs/ai-recipe-generator/tasks.md`
- 后端验证: `backend/VERIFICATION_CHECKLIST.md`
- 前端验证: `frontend/FRONTEND_VERIFICATION.md`

## 支持

如有问题，请查看:
1. 项目文档
2. 后端日志
3. 浏览器控制台

## 许可证

[根据项目实际情况填写]
