"""
会话管理服务
"""
from typing import Tuple, Optional
import uuid
import logging

from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class SessionService:
    """处理用户会话"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def generate_session_id(self) -> str:
        """
        生成唯一的会话ID
        
        Returns:
            str: UUID格式的会话ID
        """
        session_id = str(uuid.uuid4())
        logger.debug(f"生成会话ID: {session_id}")
        return session_id
    
    async def get_or_create_user(
        self,
        session_id: Optional[str]
    ) -> Tuple[str, str]:
        """
        获取或创建用户会话
        
        如果提供了有效的session_id，则查找对应的用户；
        如果session_id无效或不存在，则创建新用户和新会话。
        
        Args:
            session_id: 可选的会话ID
            
        Returns:
            Tuple[str, str]: (user_id, session_id)
        """
        try:
            # 如果提供了session_id，尝试查找用户
            if session_id:
                user = self.user_repository.get_by_session_id(session_id)
                if user:
                    logger.info(f"找到现有用户: {user.id}")
                    return user.id, user.session_id
                else:
                    logger.info(f"会话ID无效: {session_id}")
            
            # 创建新用户和新会话
            new_session_id = self.generate_session_id()
            user = self.user_repository.create_user(new_session_id)
            logger.info(f"创建新用户: {user.id}, 会话ID: {new_session_id}")
            return user.id, new_session_id
            
        except Exception as e:
            logger.error(f"获取或创建用户失败: {e}")
            raise
    
    def validate_session(self, session_id: Optional[str]) -> bool:
        """
        验证会话ID的有效性
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 会话有效返回True，否则返回False
        """
        if not session_id:
            return False
        
        try:
            user = self.user_repository.get_by_session_id(session_id)
            return user is not None
        except Exception as e:
            logger.error(f"验证会话失败: {e}")
            return False
    
    def get_user_id_by_session(self, session_id: str) -> Optional[str]:
        """
        根据会话ID获取用户ID
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[str]: 用户ID，不存在则返回None
        """
        try:
            user = self.user_repository.get_by_session_id(session_id)
            return user.id if user else None
        except Exception as e:
            logger.error(f"获取用户ID失败: {e}")
            return None
