"""
菜谱数据访问层
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging

from app.models.recipe import Recipe

logger = logging.getLogger(__name__)


class RecipeRepository:
    """菜谱数据访问"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, recipe_data: Dict[str, Any], user_id: str) -> Recipe:
        """
        创建菜谱记录
        
        Args:
            recipe_data: 菜谱数据字典
            user_id: 用户ID
            
        Returns:
            Recipe: 创建的菜谱对象
            
        Raises:
            Exception: 数据库操作失败
        """
        try:
            recipe = Recipe(
                user_id=user_id,
                name=recipe_data["name"],
                image=recipe_data.get("image"),
                ingredients=recipe_data["ingredients"],
                steps=recipe_data["steps"],
                difficulty=recipe_data["difficulty"],
                cooking_time=recipe_data["cooking_time"],
                servings=recipe_data["servings"],
                safety_tips=recipe_data.get("safety_tips")
            )
            self.db.add(recipe)
            self.db.commit()
            self.db.refresh(recipe)
            logger.info(f"创建菜谱成功: {recipe.id}")
            return recipe
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建菜谱失败: {e}")
            raise
    
    def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """
        根据ID查询菜谱
        
        Args:
            recipe_id: 菜谱ID
            
        Returns:
            Optional[Recipe]: 菜谱对象，不存在则返回None
        """
        try:
            recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
            return recipe
        except Exception as e:
            logger.error(f"查询菜谱失败: {e}")
            raise
    
    def get_by_user(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Recipe]:
        """
        查询用户的菜谱列表
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            offset: 分页偏移量
            
        Returns:
            List[Recipe]: 菜谱列表
        """
        try:
            recipes = (
                self.db.query(Recipe)
                .filter(Recipe.user_id == user_id)
                .order_by(Recipe.created_at.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )
            return recipes
        except Exception as e:
            logger.error(f"查询用户菜谱列表失败: {e}")
            raise
    
    def delete(self, recipe_id: str) -> bool:
        """
        删除菜谱
        
        Args:
            recipe_id: 菜谱ID
            
        Returns:
            bool: 删除成功返回True，菜谱不存在返回False
            
        Raises:
            Exception: 数据库操作失败
        """
        try:
            recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
            if not recipe:
                return False
            
            self.db.delete(recipe)
            self.db.commit()
            logger.info(f"删除菜谱成功: {recipe_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除菜谱失败: {e}")
            raise
    
    def count_by_user(self, user_id: str) -> int:
        """
        统计用户的菜谱数量
        
        Args:
            user_id: 用户ID
            
        Returns:
            int: 菜谱数量
        """
        try:
            count = self.db.query(Recipe).filter(Recipe.user_id == user_id).count()
            return count
        except Exception as e:
            logger.error(f"统计用户菜谱数量失败: {e}")
            raise

    
    def get_all_recipes(self, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """
        获取所有菜谱（用于搜索）
        
        Args:
            limit: 返回数量限制
            offset: 分页偏移量
            
        Returns:
            List[Recipe]: 菜谱列表
        """
        try:
            recipes = (
                self.db.query(Recipe)
                .order_by(Recipe.created_at.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )
            return recipes
        except Exception as e:
            logger.error(f"查询所有菜谱失败: {e}")
            raise
