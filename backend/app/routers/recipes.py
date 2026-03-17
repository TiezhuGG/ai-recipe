"""Recipe routes."""
from __future__ import annotations

import logging
from typing import Optional
from urllib.parse import urlparse

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
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
    SessionInitResponse,
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


def _infer_request_scheme(request: Request) -> str:
    for header_name in ('origin', 'referer'):
        header_value = request.headers.get(header_name)
        if not header_value:
            continue

        parsed = urlparse(header_value)
        if parsed.scheme:
            return parsed.scheme.lower()

    forwarded_proto = request.headers.get('x-forwarded-proto')
    if forwarded_proto:
        normalized = forwarded_proto.split(',')[0].strip().lower()
        if normalized:
            return normalized

    return request.url.scheme.lower()


def _should_use_secure_cookie(request: Request) -> bool:
    if not settings.SESSION_COOKIE_SECURE:
        return False

    return _infer_request_scheme(request) == 'https'


def _set_session_cookie(response: Response, request: Request, session_id: str) -> None:
    secure_cookie = _should_use_secure_cookie(request)
    if settings.SESSION_COOKIE_SECURE and not secure_cookie:
        logger.debug('Downgrading session cookie to non-secure for %s requests', _infer_request_scheme(request))

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        max_age=settings.SESSION_COOKIE_MAX_AGE,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        secure=secure_cookie,
        domain=settings.SESSION_COOKIE_DOMAIN or None,
        path='/',
    )


@router.get('/session/init', response_model=SessionInitResponse)
async def init_session(
    request: Request,
    response: Response,
    session_id: Optional[str] = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
    session_service: SessionService = Depends(get_session_service),
):
    try:
        _, active_session_id = await session_service.get_or_create_user(session_id)

        if active_session_id != session_id:
            _set_session_cookie(response, request, active_session_id)
            return SessionInitResponse(success=True, message='Session initialized')

        return SessionInitResponse(success=True, message='Session ready')
    except Exception as exc:
        logger.error('Session initialization failed: %s', exc)
        raise HTTPException(status_code=500, detail=f'Session initialization failed: {exc}')


@router.post('/recipes/generate', response_model=RecipeResponse)
async def generate_recipe(
    request: GenerateRecipeRequest,
    recipe_service: RecipeService = Depends(get_recipe_service),
):
    try:
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
        raise HTTPException(status_code=500, detail=f'Recipe generation failed: {exc}')


@router.post('/recipes/save', response_model=SaveRecipeResponse)
async def save_recipe(
    request: SaveRecipeRequest,
    response: Response,
    http_request: Request,
    session_id: Optional[str] = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
    recipe_service: RecipeService = Depends(get_recipe_service),
    session_service: SessionService = Depends(get_session_service),
):
    try:
        if not session_id:
            raise HTTPException(status_code=403, detail='Session missing, please refresh and try again')

        user_id = session_service.get_user_id_by_session(session_id)
        if not user_id:
            raise HTTPException(status_code=403, detail='Session expired, please refresh and try again')

        recipe_id = await recipe_service.save_recipe(request.model_dump(), user_id)
        _set_session_cookie(response, http_request, session_id)
        return SaveRecipeResponse(id=recipe_id, success=True, message='Recipe saved successfully')
    except HTTPException:
        raise
    except Exception as exc:
        logger.error('Saving recipe failed: %s', exc)
        raise HTTPException(status_code=500, detail=f'Saving recipe failed: {exc}')


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
            logger.info('Recipe history requested without session cookie')
            return RecipeHistoryResponse(recipes=[], total=0, limit=limit, offset=offset)

        user_id = session_service.get_user_id_by_session(session_id)
        if not user_id:
            logger.info('Recipe history requested with invalid session id: %s', session_id)
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
        raise HTTPException(status_code=500, detail=f'Fetching recipe history failed: {exc}')


@router.get('/recipes/{recipe_id}', response_model=RecipeResponse)
async def get_recipe_by_id(
    recipe_id: str,
    session_id: Optional[str] = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
    recipe_service: RecipeService = Depends(get_recipe_service),
    session_service: SessionService = Depends(get_session_service),
):
    try:
        if not session_id:
            raise HTTPException(status_code=403, detail='Please initialize a session first')

        user_id = session_service.get_user_id_by_session(session_id)
        if not user_id:
            raise HTTPException(status_code=403, detail='Session invalid')

        recipe = await recipe_service.get_recipe_by_id(recipe_id, user_id)
        if not recipe:
            raise HTTPException(status_code=404, detail='Recipe not found or access denied')

        return RecipeResponse(**recipe)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error('Fetching recipe detail failed: %s', exc)
        raise HTTPException(status_code=500, detail=f'Fetching recipe failed: {exc}')


@router.post('/recipes/generate-image')
async def generate_dish_image(
    request: dict,
    recipe_service: RecipeService = Depends(get_recipe_service),
):
    raise HTTPException(status_code=503, detail='Image generation is temporarily disabled')
