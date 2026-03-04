"""
生产环境配置
"""
import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).resolve().parent.parent

# 应用配置
APP_NAME = os.getenv("APP_NAME", "AI Recipe Generator")
APP_ENV = "production"
DEBUG = False

# 服务器配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://username:password@localhost:5432/recipe_db"
)

# 豆包 AI API 配置
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
DOUBAO_API_URL = os.getenv(
    "DOUBAO_API_URL",
    "https://ark.cn-beijing.volces.com/api/v3"
)

if not DOUBAO_API_KEY:
    raise ValueError("DOUBAO_API_KEY must be set in production")

# 文件上传配置
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/var/www/recipe-app/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 10485760))  # 10MB

# CORS 配置
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://yourdomain.com"
).split(",")

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "/var/log/recipe-app/app.log")

# 确保日志目录存在
log_dir = Path(LOG_FILE).parent
log_dir.mkdir(parents=True, exist_ok=True)

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in production")

# 数据库连接池配置
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 20))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 10))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", 30))

# 性能配置
WORKERS = int(os.getenv("WORKERS", 4))
