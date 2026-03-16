"""
AI recipe generator API entrypoint.
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.routers import cooking, images, recipes, search


logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle hooks."""
    logger.info("Initializing database")
    init_db()
    logger.info("Application started in %s mode", settings.APP_ENV)
    yield
    logger.info("Application shutdown complete")


app = FastAPI(
    title="AI Recipe Generator",
    description="AI powered recipe generation and cooking assistant API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(recipes.router, prefix="/api", tags=["recipes"])
app.include_router(images.router, prefix="/api", tags=["images"])
app.include_router(cooking.router, prefix="/api", tags=["cooking"])
app.include_router(search.router, prefix="/api", tags=["search"])


@app.get("/")
async def root():
    """Basic status endpoint."""
    return {
        "status": "ok",
        "message": "AI Recipe Generator API",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
