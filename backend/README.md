# Backend API

## 🧠 AI 菜谱平台后端

基于 FastAPI 构建的后端服务，负责菜谱生成、食材识别、搜索推荐、烹饪问答、会话管理与数据持久化。

## ✨ Responsibilities

- 生成结构化菜谱数据
- 保存和读取历史菜谱
- 识别上传图片中的食材
- 支持按食材搜索和智能推荐
- 提供烹饪实时问答与问题诊断
- 管理用户会话与 Cookie
- 对接 SQLite / PostgreSQL

## 🛠️ Stack

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi&logoColor=white)](../backend)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?logo=python&logoColor=white)](../backend)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-d71f00?logo=sqlalchemy&logoColor=white)](../backend)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169e1?logo=postgresql&logoColor=white)](../docker-compose.yml)

- FastAPI
- SQLAlchemy 2.x
- Pydantic / pydantic-settings
- HTTPX
- Pillow
- Uvicorn
- `psycopg[binary]`

## 📁 Structure

```text
backend/
├─ app/
│  ├─ core/              # 配置、数据库连接
│  ├─ models/            # ORM 模型
│  ├─ repositories/      # 数据访问层
│  ├─ routers/           # API 路由
│  ├─ schemas/           # 请求 / 响应模型
│  └─ services/          # AI 与业务服务
├─ config/
├─ main.py               # FastAPI 入口
├─ requirements.txt
├─ Dockerfile
└─ .env.example
```

## 🚀 Run Locally

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

本地开发默认使用 SQLite：

```env
DATABASE_URL=sqlite:///./dev.db
```

切换 PostgreSQL 时示例：

```env
DATABASE_URL=postgresql+psycopg://recipe_user:your_password@localhost:5432/recipe_db
```

### 3. Start the API server

```bash
python main.py
```

或：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Open API docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔌 API Overview

### Health

- `GET /`
- `GET /health`

### Recipes

- `GET /api/session/init`
- `POST /api/recipes/generate`
- `POST /api/recipes/save`
- `GET /api/recipes/history`
- `GET /api/recipes/{recipe_id}`
- `POST /api/recipes/generate-image`

Save/history endpoints now require a valid session cookie. Frontend should call `GET /api/session/init` before save/history requests.

说明：`generate-image` 当前返回 `503`，用于临时关闭效果图功能。

### Images

- `POST /api/images/recognize`

### Search

- `POST /api/search/ingredients`
- `POST /api/search/recommend`
- `POST /api/search/parse-dish`

### Cooking Assistant

- `POST /api/cooking/ask`
  支持流式输出，返回 `text/event-stream`
- `POST /api/cooking/diagnose`

## ⚙️ Key Environment Variables

### AI Config

- `LLM_API_KEY`
- `LLM_BASE_URL`
- `MODEL_NAME`

### Database

- `DATABASE_URL`
- `DB_POOL_SIZE`
- `DB_MAX_OVERFLOW`
- `DB_POOL_TIMEOUT`
- `DB_POOL_RECYCLE`

### App Runtime

- `APP_ENV`
- `LOG_LEVEL`
- `API_TIMEOUT`
- `API_MAX_RETRIES`
- `UVICORN_WORKERS`

### Upload / Storage

- `UPLOAD_DIR`
- `MAX_UPLOAD_SIZE`

### Session / Security

- `SECRET_KEY`
- `CORS_ORIGINS`
- `SESSION_COOKIE_NAME`
- `SESSION_COOKIE_DOMAIN`
- `SESSION_COOKIE_SECURE`
- `SESSION_COOKIE_SAMESITE`
- `SESSION_COOKIE_MAX_AGE`

## 🗄️ Database Initialization

本地运行：

```bash
python -c "from app.core.database import init_db; init_db()"
```

或在项目根目录使用脚本：

```bash
bash scripts/db-migrate.sh local
```

## 🐳 Docker Notes

生产部署时，后端服务由根目录 `docker-compose.yml` 统一启动：

```bash
bash scripts/deploy-docker.sh
```

在 Docker 环境中：

- 后端容器名：`recipe-backend`
- 数据库主机名：`db`
- 上传目录挂载到：`./backend/uploads`
- 日志目录挂载到：`./backend/logs`

## 🧪 Debug Tips

- 如果报 `ModuleNotFoundError: No module named 'psycopg'`，先重新安装 `requirements.txt`
- 如果切换到 PostgreSQL，确认 `DATABASE_URL` 使用的是 `postgresql+psycopg://`
- 如果 Cookie 不生效，检查 `SESSION_COOKIE_SECURE` 是否与当前 HTTP / HTTPS 环境匹配
- 如果前端访问失败，优先看 `CORS_ORIGINS` 和 Docker 健康检查日志

## 📄 Related Docs

- [Root README](../README.md)
- [Frontend README](../frontend/README.md)
