"""
菜谱数据模型
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Recipe(Base):
    """菜谱表"""
    __tablename__ = "recipes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    image = Column(String(500), nullable=True)
    
    # 使用JSON存储复杂结构
    ingredients = Column(JSON, nullable=False)  # {main: [...], secondary: [...]}
    steps = Column(JSON, nullable=False)  # [{order, description, image}, ...]
    
    difficulty = Column(String(20), nullable=False)  # easy, medium, hard
    cooking_time = Column(Integer, nullable=False)  # 分钟
    servings = Column(Integer, nullable=False)
    safety_tips = Column(JSON, nullable=True)  # [tip1, tip2, ...]
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # 关系：每个菜谱属于一个用户
    user = relationship("User", back_populates="recipes")
    
    def __repr__(self):
        return f"<Recipe(id={self.id}, name={self.name}, user_id={self.user_id})>"
