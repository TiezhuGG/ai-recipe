#!/bin/bash
# Docker 部署脚本

set -e

echo "🐳 开始 Docker 部署..."

# 检查 Docker 和 Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env 文件不存在，创建默认配置..."
    cat > .env << EOF
# 数据库配置
DB_PASSWORD=change_me_in_production

# 豆包 API 配置
LLM_API_KEY=your_api_key_here
DOUBAO_API_URL=https://ark.cn-beijing.volces.com/api/v3

# 安全配置
SECRET_KEY=change_me_in_production

# 前端配置
VITE_API_BASE_URL=http://localhost:8000
EOF
    echo "⚠️  请编辑 .env 文件并填入正确的配置"
    exit 1
fi

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down

# 构建镜像
echo "🔨 构建 Docker 镜像..."
docker-compose build

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 显示日志
echo "📋 服务日志:"
docker-compose logs --tail=50

echo "✅ Docker 部署完成！"
echo "🌐 前端地址: http://localhost"
echo "🔌 后端地址: http://localhost:8000"
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
