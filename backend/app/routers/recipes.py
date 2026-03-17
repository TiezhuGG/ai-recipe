"""Recipe routes."""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.repositories.recipe_repository import RecipeRepository
from app.repositories.user_repository import UserRepository
from app.schemas.recipe_schemas import (
    GenerateRecipeRequest,
    RecipeHistoryResponse,
    RecipeListItem,
    RecipeResponse,
    SaveRecipeRequest,
    SaveRecipeResponse,
)
from app.services.ai_service import AIService
from app.services.recipe_service import RecipeService
from app.services.session_service import SessionService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_recipe_service(db: Session = Depends(get_db)) -> RecipeService:
    ai_service = AIService()
    recipe_repository = RecipeRepository(db)
    return RecipeService(ai_service, recipe_repository)


def get_session_service(db: Session = Depends(get_db)) -> SessionService:
    user_repository = UserRepository(db)
    return SessionService(user_repository)


@router.post('/recipes/generate', response_model=RecipeResponse)
async def generate_recipe(
    request: GenerateRecipeRequest,
    response: Response,
    session_id: Optional[str] = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
    recipe_service: RecipeService = Depends(get_recipe_service),
    session_service: SessionService = Depends(get_session_service),
):
    try:
        user_id, new_session_id = await session_service.get_or_create_user(session_id)

        if new_session_id != session_id:
            response.set_cookie(
                key=settings.SESSION_COOKIE_NAME,
                value=new_session_id,
                httponly=True,
                max_age=settings.SESSION_COOKIE_MAX_AGE,
                samesite=settings.SESSION_COOKIE_SAMESITE,
                secure=settings.SESSION_COOKIE_SECURE,
                domain=settings.SESSION_COOKIE_DOMAIN or None,
                path='/',
            )

        recipe_data = await recipe_service.generate_recipe(
            ingredients=request.ingredients,
            flavor_tags=request.flavor_tags,
            cuisine_types=request.cuisine_types,
            special_groups=request.special_groups,
            recognized_ingredients=request.recognized_ingredients,
            recipe_name=request.recipe_name,
        )

        return RecipeResponse(**recipe_data)
    except ValueError as exc:
        logger.warning('Recipe generation validation failed: %s', exc)
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error('Recipe generation failed: %s', exc)
        raise HTTPException(status_code=500, detail=f'生成菜谱失败: {exc}')


@router.post('/recipes/save', response_model=SaveRecipeResponse)
async def save_recipe(
    request: SaveRecipeRequest,
    response: Response,
    session_id: Optional[str] = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
    recipe_service: RecipeService = Depends(get_recipe_service),
    session_service: SessionService = Depends(get_session_service),
):
    try:
        user_id, new_session_id = await session_service.get_or_create_user(session_id)

        if new_session_id != session_id:
            response.set_cookie(
                key=settings.SESSION_COOKIE_NAME,
                value=new_session_id,
                httponly=True,
                max_age=settings.SESSION_COOKIE_MAX_AGE,
                samesite=settings.SESSION_COOKIE_SAMESITE,
                secure=settings.SESSION_COOKIE_SECURE,
                domain=settings.SESSION_COOKIE_DOMAIN or None,
                path='/',
            )

        recipe_id = await recipe_service.save_recipe(request.model_dump(), user_id)
        return SaveRecipeResponse(id=recipe_id, success=True, message='菜谱保存成功')
    except HTTPException:
        raise
    except Exception as exc:
        logger.error('Saving recipe failed: %s', exc)
        raise HTTPException(status_code=500, detail=f'保存菜谱失败: {exc}')


@router.get('/recipes/history', response_model=RecipeHistoryResponse)
async def get_recipe_history(
    limit: int = 50,
    offset: int = 0,
    session_id: Optional[str] = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
    recipe_service: RecipeService = Depends(get_recipe_service),
    session_service: SessionService = Depends(get_session_service),
):
    try:
        if not session_id:
            return RecipeHistoryResponse(recipes=[], total=0, limit=limit, offset=offset)

        user_id = session_service.get_user_id_by_session(session_id)
        if not user_id:
            return RecipeHistoryResponse(recipes=[], total=0, limit=limit, offset=offset)

        recipes = await recipe_service.get_user_recipes(user_id, limit, offset)
        total = await recipe_service.get_user_recipe_count(user_id)
        recipe_items = [RecipeListItem(**recipe) for recipe in recipes]

        return RecipeHistoryResponse(
            recipes=recipe_items,
            total=total,
            limit=limit,
            offset=offset,
        )
    except Exception as exc:
        logger.error('Fetching recipe history failed: %s', exc)
        raise HTTPException(status_code=500, detail=f'获取历史菜谱失败: {exc}')


@router.get('/recipes/{recipe_id}', response_model=RecipeResponse)
async def get_recipe_by_id(
    recipe_id: str,
    session_id: Optional[str] = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
    recipe_service: RecipeService = Depends(get_recipe_service),
    session_service: SessionService = Depends(get_session_service),
):
    try:
        if not session_id:
            raise HTTPException(status_code=403, detail='请先登录')

        user_id = session_service.get_user_id_by_session(session_id)
        if not user_id:
            raise HTTPException(status_code=403, detail='会话无效')

        recipe = await recipe_service.get_recipe_by_id(recipe_id, user_id)
        if not recipe:
            raise HTTPException(status_code=404, detail='菜谱不存在或无权访问')

        return RecipeResponse(**recipe)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error('Fetching recipe detail failed: %s', exc)
        raise HTTPException(status_code=500, detail=f'获取菜谱失败: {exc}')


@router.post('/recipes/generate-image')
async def generate_dish_image(
    request: dict,
    recipe_service: RecipeService = Depends(get_recipe_service),
):
    raise HTTPException(status_code=503, detail='效果图功能已暂时关闭')
