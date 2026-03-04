#!/bin/bash
# 数据库迁移脚本

set -e

echo "🗄️  开始数据库迁移..."

# 进入后端目录
cd backend

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 运行数据库初始化
echo "📊 初始化数据库表..."
python -c "
from app.core.database import init_db
init_db()
print('✅ 数据库初始化完成')
"

echo "✅ 数据库迁移完成！"
