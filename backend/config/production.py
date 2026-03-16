"""
Production configuration.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

APP_NAME = os.getenv("APP_NAME", "AI Recipe Generator")
APP_ENV = "production"
DEBUG = False

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://username:password@localhost:5432/recipe_db"
)

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL") or os.getenv("LLM_API_BASE_URL") or os.getenv("DOUBAO_API_URL") or "https://api-inference.modelscope.cn/v1"
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen3.5-35B-A3B")
IMAGE_MODEL_NAME = os.getenv("IMAGE_MODEL_NAME", "")

if not LLM_API_KEY:
    raise ValueError("LLM_API_KEY must be set in production")

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/var/www/recipe-app/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 10485760))

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://yourdomain.com"
).split(",")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "/var/log/recipe-app/app.log")

log_dir = Path(LOG_FILE).parent
log_dir.mkdir(parents=True, exist_ok=True)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in production")

DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 20))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 10))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", 30))

WORKERS = int(os.getenv("WORKERS", 4))
