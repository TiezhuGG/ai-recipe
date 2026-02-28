"""
菜谱相关路由
"""
from fastapi import APIRouter, Depends, Cookie, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.schemas.recipe_schemas import (
    GenerateRecipeRequest,
    RecipeResponse,
    SaveRecipeRequest,
    SaveRecipeResponse,
    RecipeHistoryResponse,
    RecipeListItem,
    ErrorResponse
)
from app.services.recipe_service import RecipeService
from app.services.ai_service import AIService
from app.services.session_service import SessionService
from app.repositories.recipe_repository import RecipeRepository
from app.repositories.user_repository import UserRepository

router = APIRouter()
logger = logging.getLogger(__name__)


def get_recipe_service(db: Session = Depends(get_db)) -> RecipeService:
    """获取RecipeService实例"""
    ai_service = AIService()
    recipe_repository = RecipeRepository(db)
    return RecipeService(ai_service, recipe_repository)


def get_session_service(db: Session = Depends(get_db)) -> SessionService:
    """获取SessionService实例"""
    user_repository = UserRepository(db)
    return SessionService(user_repository)


@router.post("/recipes/generate", response_model=RecipeResponse)
async def generate_recipe(
    request: GenerateRecipeRequest,
    response: Response,
    session_id: Optional[str] = Cookie(None),
    recipe_service: RecipeService = Depends(get_recipe_service),
    session_service: SessionService = Depends(get_session_service)
):
    """
    生成AI菜谱
    
    Args:
        request: 包含食材、口味、菜系等信息的请求体
        session_id: 用户会话ID（从Cookie获取）
        
    Returns:
        RecipeResponse: 生成的菜谱数据
        
    Raises:
        400: 请求参数无效
        500: AI服务调用失败
    """
    try:
        # 获取或创建用户会话
        user_id, new_session_id = await session_service.get_or_create_user(session_id)
        
        # 如果是新会话，设置Cookie
        if new_session_id != session_id:
            response.set_cookie(
                key="session_id",
                value=new_session_id,
                httponly=True,
                max_age=30 * 24 * 60 * 60,  # 30天
                samesite="lax"
            )
        
        # 生成菜谱
        recipe_data = await recipe_service.generate_recipe(
            ingredients=request.ingredients,
            flavor_tags=request.flavor_tags,
            cuisine_types=request.cuisine_types,
            special_groups=request.special_groups,
            recognized_ingredients=request.recognized_ingredients
        )
        
        return RecipeResponse(**recipe_data)
        
    except ValueError as e:
        logger.warning(f"参数验证失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"生成菜谱失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成菜谱失败: {str(e)}")


@router.post("/recipes/save", response_model=SaveRecipeResponse)
async def save_recipe(
    request: SaveRecipeRequest,
    session_id: Optional[str] = Cookie(None),
    recipe_service: RecipeService = Depends(get_recipe_service),
    session_service: SessionService = Depends(get_session_service),
    db: Session = Depends(get_db)
):
    """
    保存菜谱到用户历史
    
    Args:
        request: 要保存的菜谱数据
        session_id: 用户会话ID
        
    Returns:
        SaveRecipeResponse: 保存结果和菜谱ID
        
    Raises:
        400: 菜谱数据无效或未登录
        500: 数据库保存失败
    """
    try:
        # 验证会话
        if not session_id:
            raise HTTPException(status_code=400, detail="请先生成菜谱")
        
        user_id = session_service.get_user_id_by_session(session_id)
        if not user_id:
            raise HTTPException(status_code=400, detail="会话无效，请重新生成菜谱")
        
        # 保存菜谱
        recipe_data = request.model_dump()
        recipe_id = await recipe_service.save_recipe(recipe_data, user_id)
        
        return SaveRecipeResponse(
            id=recipe_id,
            success=True,
            message="菜谱保存成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存菜谱失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存菜谱失败: {str(e)}")


@router.get("/recipes/history", response_model=RecipeHistoryResponse)
async def get_recipe_history(
    limit: int = 50,
    offset: int = 0,
    session_id: Optional[str] = Cookie(None),
    recipe_service: RecipeService = Depends(get_recipe_service),
    session_service: SessionService = Depends(get_session_service)
):
    """
    获取用户的历史菜谱列表
    
    Args:
        session_id: 用户会话ID
        limit: 返回数量限制
        offset: 分页偏移量
        
    Returns:
        RecipeHistoryResponse: 菜谱列表
    """
    try:
        # 验证会话
        if not session_id:
            return RecipeHistoryResponse(recipes=[], total=0, limit=limit, offset=offset)
        
        user_id = session_service.get_user_id_by_session(session_id)
        if not user_id:
            return RecipeHistoryResponse(recipes=[], total=0, limit=limit, offset=offset)
        
        # 获取菜谱列表
        recipes = await recipe_service.get_user_recipes(user_id, limit, offset)
        
        # 转换为响应模型
        recipe_items = [RecipeListItem(**recipe) for recipe in recipes]
        
        return RecipeHistoryResponse(
            recipes=recipe_items,
            total=len(recipe_items),
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"获取历史菜谱失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取历史菜谱失败: {str(e)}")


@router.get("/recipes/{recipe_id}", response_model=RecipeResponse)
async def get_recipe_by_id(
    recipe_id: str,
    session_id: Optional[str] = Cookie(None),
    recipe_service: RecipeService = Depends(get_recipe_service),
    session_service: SessionService = Depends(get_session_service)
):
    """
    根据ID获取菜谱详情
    
    Args:
        recipe_id: 菜谱ID
        session_id: 用户会话ID
        
    Returns:
        RecipeResponse: 菜谱详情
        
    Raises:
        404: 菜谱不存在
        403: 无权访问该菜谱
    """
    try:
        # 验证会话
        if not session_id:
            raise HTTPException(status_code=403, detail="请先登录")
        
        user_id = session_service.get_user_id_by_session(session_id)
        if not user_id:
            raise HTTPException(status_code=403, detail="会话无效")
        
        # 获取菜谱详情
        recipe = await recipe_service.get_recipe_by_id(recipe_id, user_id)
        
        if not recipe:
            raise HTTPException(status_code=404, detail="菜谱不存在或无权访问")
        
        return RecipeResponse(**recipe)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取菜谱详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取菜谱失败: {str(e)}")
