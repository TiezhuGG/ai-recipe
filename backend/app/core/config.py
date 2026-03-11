"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    # 豆包API配置
    LLM_API_KEY: str = ""
    LLM_API_BASE_URL: str = ""
    MODEL_NAME: str = ""
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./dev.db"
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    # API超时配置
    API_TIMEOUT: int = 120
    API_MAX_RETRIES: int = 2
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
