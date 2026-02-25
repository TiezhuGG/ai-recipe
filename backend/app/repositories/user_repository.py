"""
用户数据访问层
"""
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.models.user import User

logger = logging.getLogger(__name__)


class UserRepository:
    """用户数据访问"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, session_id: str) -> User:
        """
        创建新用户
        
        Args:
            session_id: 会话ID
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            Exception: 数据库操作失败
        """
        try:
            user = User(session_id=session_id)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"创建用户成功: {user.id}")
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建用户失败: {e}")
            raise
    
    def get_by_session_id(self, session_id: str) -> Optional[User]:
        """
        根据会话ID查询用户
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[User]: 用户对象，不存在则返回None
        """
        try:
            user = self.db.query(User).filter(User.session_id == session_id).first()
            return user
        except Exception as e:
            logger.error(f"查询用户失败: {e}")
            raise
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        根据用户ID查询用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[User]: 用户对象，不存在则返回None
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            return user
        except Exception as e:
            logger.error(f"查询用户失败: {e}")
            raise
