# 后端设置和测试指南

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量示例文件：

```bash
copy .env.example .env
```

编辑 `.env` 文件，填写必要的配置：

```env
# 豆包API配置（必需）
LLM_API_KEY=your_api_key_here
LLM_API_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# 数据库配置（可选，默认使用SQLite）
DATABASE_URL=sqlite:///./dev.db

# 文件上传配置（可选）
UPLOAD_DIR=./uploads

# CORS配置（可选）
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**重要**: 必须配置有效的 `LLM_API_KEY` 才能使用AI功能。

### 3. 启动服务器

```bash
python main.py
```

或使用uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务器将在 http://localhost:8000 启动。

### 4. 访问API文档

启动后，访问以下URL查看自动生成的API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 测试API

### 方法1: 使用测试脚本

运行自动化测试脚本：

```bash
python test_api.py
```

这将测试所有主要API端点。

### 方法2: 使用Swagger UI

1. 访问 http://localhost:8000/docs
2. 点击任意端点
3. 点击 "Try it out"
4. 填写参数
5. 点击 "Execute"

### 方法3: 使用curl

#### 健康检查
```bash
curl http://localhost:8000/
```

#### 生成菜谱
```bash
curl -X POST http://localhost:8000/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d "{\"ingredients\": [\"鸡胸肉\", \"西兰花\"], \"flavor_tags\": [\"健康\"], \"cuisine_types\": [\"中餐\"], \"special_groups\": []}"
```

#### 查询历史（需要先生成菜谱获取session_id）
```bash
curl http://localhost:8000/api/recipes/history \
  -H "Cookie: session_id=YOUR_SESSION_ID"
```

## 验证清单

在继续前端开发之前，请确认以下功能正常：

- [ ] 服务器成功启动，无错误
- [ ] 数据库表自动创建
- [ ] 健康检查端点返回200
- [ ] 菜谱生成端点正常工作（需要有效的API密钥）
- [ ] 会话管理正常（Cookie设置）
- [ ] 菜谱保存功能正常
- [ ] 历史记录查询正常
- [ ] 菜谱详情查询正常
- [ ] 图片上传端点可访问（即使AI识别可能失败）

## 常见问题

### 1. 数据库错误

如果遇到数据库错误，删除数据库文件重新创建：

```bash
del dev.db  # Windows
rm dev.db   # Linux/Mac
```

然后重启服务器。

### 2. 豆包API错误

确保：
- API密钥正确
- API基础URL正确
- 网络连接正常
- API配额充足

### 3. 端口被占用

如果8000端口被占用，可以使用其他端口：

```bash
uvicorn main:app --reload --port 8001
```

### 4. 模块导入错误

确保在backend目录下运行命令，或设置PYTHONPATH：

```bash
set PYTHONPATH=%CD%  # Windows
export PYTHONPATH=$(pwd)  # Linux/Mac
```

## 下一步

后端验证通过后，可以继续：

1. 任务9: 搭建前端项目基础架构
2. 开发前端组件
3. 集成前后端

## 技术支持

如有问题，请检查：
1. 日志输出（控制台）
2. API文档（/docs）
3. 环境变量配置
4. 依赖包版本
