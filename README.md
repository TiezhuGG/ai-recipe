# AI Smart Cookbook Platform

<div align="center">

# 🍳 AI 智能生成菜谱平台

一套面向真实做饭场景的 AI 全栈应用，支持菜谱生成、食材识别、随料大搜、烹饪问答、历史记录与 Docker 化部署。

[![Vue 3](https://img.shields.io/badge/Vue-3.4-42b883?logo=vue.js&logoColor=white)](./frontend)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi&logoColor=white)](./backend)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178c6?logo=typescript&logoColor=white)](./frontend)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?logo=python&logoColor=white)](./backend)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169e1?logo=postgresql&logoColor=white)](./docker-compose.yml)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ed?logo=docker&logoColor=white)](./docker-compose.yml)

</div>

## ✨ Features

- `AI 菜谱生成`：根据食材、口味、菜系和特殊人群需求生成结构化菜谱。
- `食材识别`：上传图片后识别食材，并继续流转到菜谱生成流程。
- `随料大搜`：按现有食材搜索菜谱、获取搭配推荐、解析目标菜品所需食材。
- `烹饪学堂`：支持实时问答和烹饪问题诊断，适合边做边问。
- `美食盲盒`：随机菜品/主厨推荐，适合“今天吃什么”的轻决策场景。
- `历史记录`：保存已生成菜谱，支持详情回看。
- `Docker 部署`：内置 PostgreSQL、前后端容器和常用运维脚本。

## 🧭 Current Status

### 已完成模块

- 首页 AI 菜谱生成
- 图片识别食材
- 随料大搜
- 烹饪学堂
- 美食盲盒
- 菜谱历史记录与详情页
- Docker Compose 部署与健康检查脚本


## 🏗️ Project Structure

```text
cookbook/
├─ frontend/              # Vue 3 + TypeScript + Vite 前端
├─ backend/               # FastAPI + SQLAlchemy 后端
├─ scripts/               # 部署、监控、备份、迁移脚本
├─ docker-compose.yml     # 生产部署编排
├─ .env.example           # 根目录生产环境变量模板
└─ README.md
```

## 🛠️ Tech Stack

### Frontend

- Vue 3
- TypeScript
- Vite
- Vue Router
- Axios
- Tailwind CSS

### Backend

- FastAPI
- SQLAlchemy
- Pydantic Settings
- HTTPX
- Pillow
- PostgreSQL / SQLite

### DevOps

- Docker Compose
- Nginx
- PostgreSQL 15
- Bash deployment scripts

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd cookbook
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

按需填写以下核心配置：

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `MODEL_NAME`
- `SECRET_KEY`

### 3. Run with Docker

```bash
bash scripts/deploy-docker.sh
```

部署完成后默认访问：

- Frontend: `http://localhost:8081`
- Backend: `http://localhost:8081/health`
- API Docs: `http://localhost:8081/docs`

### 4. Verify services

```bash
bash scripts/health-check.sh
```

## 💻 Local Development

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
python main.py
```

默认情况下：

- 前端开发地址：`http://localhost:5173`
- 后端开发地址：`http://localhost:8000`
- 本地开发数据库：`SQLite`

## 🐘 Database Strategy

- `开发环境`：推荐使用 SQLite，配置简单，适合单机调试。
- `生产环境`：推荐使用 PostgreSQL，通过 `docker-compose.yml` 启动。

数据库初始化：

```bash
bash scripts/db-migrate.sh
```

数据库备份：

```bash
bash scripts/backup-db.sh
```

## 📡 Core Pages

- `/`：AI 菜谱生成首页
- `/blind-box`：美食盲盒
- `/cooking-school`：烹饪学堂
- `/search`：随料大搜
- `/history`：历史菜谱
- `/recipe/:id`：菜谱详情

## 🔌 Core API

### Recipes

- `GET /api/session/init`
- `POST /api/recipes/generate`
- `POST /api/recipes/save`
- `GET /api/recipes/history`
- `GET /api/recipes/{recipe_id}`
- `POST /api/recipes/generate-image` `暂时关闭`

### Images

- `POST /api/images/recognize`

### Search

- `POST /api/search/ingredients`
- `POST /api/search/recommend`
- `POST /api/search/parse-dish`

### Cooking Assistant

- `POST /api/cooking/ask`
- `POST /api/cooking/diagnose`

## 📦 Deployment Scripts

项目内置常用运维脚本，推荐配合 Docker 使用：

- `scripts/deploy-docker.sh`：构建并启动整套服务
- `scripts/quick-deploy.sh`：部署后自动执行健康检查
- `scripts/health-check.sh`：检查前端、后端、数据库健康状态
- `scripts/monitor.sh`：查看容器、日志、资源使用情况
- `scripts/db-migrate.sh`：初始化数据库结构
- `scripts/backup-db.sh`：备份 PostgreSQL 数据库

## 🔐 Environment Files

- 根目录 `.env.example`：Docker / 生产部署模板
- `backend/.env.example`：后端本地开发模板

说明：

- Docker 部署时，优先使用项目根目录 `.env`
- 本地直接运行后端时，优先使用 `backend/.env`

## 📚 Subproject Docs

- [Frontend README](./frontend/README.md)
- [Backend README](./backend/README.md)

## 🤝 Recommended Workflow

1. 本地先使用 SQLite 验证功能。
2. 再切换 PostgreSQL 进行联调。
3. 使用 Docker Compose 进行预发布测试。
4. 最后部署到云服务器并接入域名 / HTTPS。

## 📄 License

当前仓库未声明开源许可证。如计划公开发布，建议补充 `LICENSE` 文件。
