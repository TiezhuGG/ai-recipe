#!/bin/bash
# 健康检查脚本

set -e

echo "🏥 开始健康检查..."

# 检查后端
echo "🔍 检查后端服务..."
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

if curl -f -s "${BACKEND_URL}/health" > /dev/null; then
    echo "✅ 后端服务正常"
else
    echo "❌ 后端服务异常"
    exit 1
fi

# 检查前端
echo "🔍 检查前端服务..."
FRONTEND_URL="${FRONTEND_URL:-http://localhost:5173}"

if curl -f -s "${FRONTEND_URL}" > /dev/null; then
    echo "✅ 前端服务正常"
else
    echo "❌ 前端服务异常"
    exit 1
fi

# 检查数据库连接（如果使用 Docker）
if command -v docker &> /dev/null; then
    if docker ps | grep -q recipe-db; then
        echo "✅ 数据库容器运行中"
    fi
fi

echo "✅ 所有服务健康检查通过！"
