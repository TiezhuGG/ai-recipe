"""
食材搜索相关路由
"""
from fastapi import APIRouter, Depends, HTTPException
import logging

from app.services.ai_service import AIService
from app.services.recipe_service import RecipeService
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)


def get_ai_service() -> AIService:
    """获取AIService实例"""
    return AIService()


def get_recipe_service(db: Session = Depends(get_db)) -> RecipeService:
    """获取RecipeService实例"""
    from app.repositories.recipe_repository import RecipeRepository
    ai_service = AIService()
    recipe_repository = RecipeRepository(db)
    return RecipeService(ai_service, recipe_repository)


@router.post("/search/ingredients")
async def search_by_ingredients(
    request: dict,
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """
    根据食材搜索菜谱
    
    Args:
        request: 包含ingredients的请求体
        
    Returns:
        dict: 包含recipes的响应
    """
    try:
        ingredients = request.get('ingredients', [])
        
        if not ingredients:
            raise HTTPException(status_code=400, detail="食材列表不能为空")
        
        logger.info(f"搜索食材: {ingredients}")
        
        # 从数据库搜索匹配的菜谱
        recipes = await recipe_service.search_recipes_by_ingredients(ingredients)
        
        logger.info(f"找到 {len(recipes)} 个匹配的菜谱")
        
        return {
            "success": True,
            "recipes": recipes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索菜谱失败: {e.__class__.__name__} - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"搜索服务调用失败: {str(e)}")



@router.post("/search/recommend")
async def get_ingredient_recommendation(
    request: dict,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    获取食材推荐
    
    Args:
        request: 包含ingredients的请求体
        
    Returns:
        dict: 包含recommendation的响应
    """
    try:
        ingredients = request.get('ingredients', [])
        
        if not ingredients:
            raise HTTPException(status_code=400, detail="食材列表不能为空")
        
        logger.info(f"获取食材推荐: {ingredients}")
        
        # 调用AI服务获取推荐
        recommendation = await ai_service.get_ingredient_recommendation(ingredients)
        
        logger.info(f"成功获取推荐")
        
        return {
            "success": True,
            "recommendation": recommendation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取推荐失败: {e.__class__.__name__} - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"推荐服务调用失败: {str(e)}")


@router.post("/search/parse-dish")
async def parse_dish_ingredients(
    request: dict,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    解析菜谱所需食材
    
    Args:
        request: 包含dishName的请求体
        
    Returns:
        dict: 包含菜谱信息和食材列表
    """
    try:
        dish_name = request.get('dishName', '')
        
        if not dish_name:
            raise HTTPException(status_code=400, detail="菜谱名称不能为空")
        
        logger.info(f"解析菜谱: {dish_name}")
        
        # 调用AI服务解析菜谱
        dish_info = await ai_service.parse_dish_ingredients(dish_name)
        
        logger.info(f"成功解析菜谱")
        
        return {
            "success": True,
            "dishInfo": dish_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"解析菜谱失败: {e.__class__.__name__} - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"解析服务调用失败: {str(e)}")

