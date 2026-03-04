#!/bin/bash
# 后端启动脚本

set -e

echo "🚀 启动后端服务..."

# 进入后端目录
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env 文件不存在，使用 .env.example"
    cp .env.example .env
fi

# 创建必要的目录
mkdir -p uploads logs

# 启动服务
echo "🚀 启动 FastAPI 服务..."
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
