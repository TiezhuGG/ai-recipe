"""
AI智能菜谱生成平台 - 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.routers import recipes, images, cooking

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    logger.info("初始化数据库...")
    init_db()
    logger.info("数据库初始化完成")
    yield
    # 关闭时清理资源
    logger.info("应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title="AI智能菜谱生成平台",
    description="基于豆包AI的智能菜谱生成和管理系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(recipes.router, prefix="/api", tags=["recipes"])
app.include_router(images.router, prefix="/api", tags=["images"])
app.include_router(cooking.router, prefix="/api", tags=["cooking"])


@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "status": "ok",
        "message": "AI智能菜谱生成平台API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
