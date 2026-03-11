# AI智能菜谱生成平台 - 后端

基于FastAPI的AI智能菜谱生成平台后端服务。

## 技术栈

- Python 3.10+
- FastAPI 0.104+
- SQLAlchemy 2.0+
- Pydantic 2.5+
- Uvicorn

## 项目结构

```
backend/
├── app/
│   ├── core/           # 核心配置和数据库
│   ├── models/         # SQLAlchemy数据模型
│   ├── schemas/        # Pydantic模型
│   ├── routers/        # API路由
│   ├── services/       # 业务逻辑层
│   └── repositories/   # 数据访问层
├── main.py            # 应用入口
├── requirements.txt   # 依赖包
└── .env.example      # 环境变量示例
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写豆包API密钥等配置。

### 3. 运行开发服务器

```bash
python main.py
```

或使用uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API端点

### 健康检查
- `GET /` - 根路径
- `GET /health` - 健康检查

### 菜谱相关
- `POST /api/recipes/generate` - 生成菜谱
- `POST /api/recipes/save` - 保存菜谱
- `GET /api/recipes/history` - 获取历史菜谱
- `GET /api/recipes/{recipe_id}` - 获取菜谱详情

### 图片相关
- `POST /api/images/recognize` - 识别图片中的食材

## 开发说明

1. 所有API路由在 `app/routers/` 目录下
2. 业务逻辑在 `app/services/` 目录下
3. 数据访问在 `app/repositories/` 目录下
4. 数据模型在 `app/models/` 目录下
5. 请求/响应模型在 `app/schemas/` 目录下

## 环境变量说明

- `LLM_API_KEY`: 豆包API密钥
- `LLM_API_BASE_URL`: 豆包API基础URL
- `DATABASE_URL`: 数据库连接URL
- `UPLOAD_DIR`: 文件上传目录
- `SECRET_KEY`: 应用密钥
- `CORS_ORIGINS`: 允许的跨域源
