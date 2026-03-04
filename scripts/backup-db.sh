#!/bin/bash
# 数据库备份脚本

set -e

echo "💾 开始数据库备份..."

# 配置
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/recipe_db_${TIMESTAMP}.sql"

# 创建备份目录
mkdir -p "${BACKUP_DIR}"

# 检查是否使用 Docker
if docker ps | grep -q recipe-db; then
    echo "🐳 使用 Docker 备份..."
    docker exec recipe-db pg_dump -U recipe_user recipe_db > "${BACKUP_FILE}"
else
    echo "💻 使用本地 PostgreSQL 备份..."
    # 从环境变量读取数据库配置
    DB_USER="${DB_USER:-recipe_user}"
    DB_NAME="${DB_NAME:-recipe_db}"
    DB_HOST="${DB_HOST:-localhost}"
    
    pg_dump -U "${DB_USER}" -h "${DB_HOST}" "${DB_NAME}" > "${BACKUP_FILE}"
fi

# 压缩备份文件
echo "🗜️  压缩备份文件..."
gzip "${BACKUP_FILE}"

echo "✅ 数据库备份完成: ${BACKUP_FILE}.gz"

# 清理旧备份（保留最近7天）
echo "🧹 清理旧备份..."
find "${BACKUP_DIR}" -name "recipe_db_*.sql.gz" -mtime +7 -delete

echo "✅ 备份任务完成！"
