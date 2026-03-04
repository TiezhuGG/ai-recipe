#!/bin/bash
# 前端构建脚本

set -e

echo "🚀 开始构建前端..."

# 进入前端目录
cd frontend

# 安装依赖
echo "📦 安装依赖..."
npm ci

# 运行构建
echo "🔨 构建生产版本..."
npm run build

echo "✅ 前端构建完成！"
echo "📁 构建产物位于: frontend/dist"
