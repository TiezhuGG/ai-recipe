"""Recipe domain service."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.repositories.recipe_repository import RecipeRepository
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class RecipeService:
    """Business logic for recipe workflows."""

    SAFETY_TIPS = {
        '儿童': [
            '食材尽量切小块，避免噎食风险。',
            '少盐少辣，调味尽量清淡。',
            '确保肉类和蛋类充分加热后再食用。',
            '注意出锅温度，避免烫伤。',
        ],
        '老人': [
            '食材建议切碎或炖软，方便咀嚼和消化。',
            '控制盐和油脂摄入。',
            '避免过硬、过黏、过辣的做法。',
            '优先选择新鲜、易消化的食材。',
        ],
        '孕妇': [
            '避免生食、半生食和未熟透的蛋肉海鲜。',
            '处理食材前后注意清洁，避免交叉污染。',
            '避免高汞鱼类和来源不明的食材。',
            '控制咖啡因和高糖调味品摄入。',
        ],
        '糖尿病患者': [
            '注意主食和高糖配料的总量控制。',
            '优先选择低糖、低 GI 的搭配。',
            '少用勾芡、糖醋、蜂蜜等高糖做法。',
            '建议搭配优质蛋白和蔬菜。',
        ],
        '高血压患者': [
            '减少盐、酱油、豆瓣酱等高钠调味。',
            '避免重油重盐和腌制食物。',
            '多搭配富含钾的蔬菜。',
            '烹饪方式优先蒸、煮、炖。',
        ],
    }

    def __init__(self, ai_service: AIService, recipe_repository: RecipeRepository):
        self.ai_service = ai_service
        self.recipe_repository = recipe_repository

    def _validate_generate_params(
        self,
        ingredients: List[str],
        recognized_ingredients: Optional[List[str]] = None,
    ) -> tuple[bool, Optional[str]]:
        has_ingredients = bool(ingredients)
        has_recognized = bool(recognized_ingredients)

        if not has_ingredients and not has_recognized:
            return False, '请至少提供一种食材，或上传食材图片。'

        all_ingredients = (ingredients or []) + (recognized_ingredients or [])
        for ingredient in all_ingredients:
            if not ingredient or not ingredient.strip():
                return False, '食材名称不能为空。'

        return True, None

    def _add_safety_tips(self, recipe_data: Dict[str, Any], special_groups: List[str]) -> Dict[str, Any]:
        if not special_groups:
            return recipe_data

        safety_tips: List[str] = []
        for group in special_groups:
            tips = self.SAFETY_TIPS.get(group)
            if not tips:
                continue
            safety_tips.append(f'{group}注意事项：')
            safety_tips.extend(tips)

        existing_tips = recipe_data.get('safety_tips')
        if isinstance(existing_tips, list):
            safety_tips.extend(existing_tips)

        recipe_data['safety_tips'] = safety_tips or None
        return recipe_data

    async def generate_recipe(
        self,
        ingredients: List[str],
        flavor_tags: List[str],
        cuisine_types: List[str],
        special_groups: List[str],
        recognized_ingredients: Optional[List[str]] = None,
        recipe_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        is_valid, error_message = self._validate_generate_params(ingredients, recognized_ingredients)
        if not is_valid:
            logger.warning('Recipe generation params invalid: %s', error_message)
            raise ValueError(error_message)

        all_ingredients = list(dict.fromkeys((ingredients or []) + (recognized_ingredients or [])))
        logger.info(
            'Generating recipe with ingredients=%s flavor_tags=%s cuisine_types=%s recipe_name=%s',
            all_ingredients,
            flavor_tags,
            cuisine_types,
            recipe_name,
        )

        try:
            recipe_data = await self.ai_service.generate_recipe(
                ingredients=all_ingredients,
                flavor_tags=flavor_tags,
                cuisine_types=cuisine_types,
                special_groups=special_groups,
                recipe_name=recipe_name,
            )
        except Exception as exc:
            logger.error('AI recipe generation failed: %s', exc)
            raise Exception(f'生成菜谱失败: {exc}')

        recipe_data = self._add_safety_tips(recipe_data, special_groups)
        logger.info('Recipe generated successfully: %s', recipe_data.get('name'))
        return recipe_data

    async def save_recipe(self, recipe_data: Dict[str, Any], user_id: str) -> str:
        try:
            recipe = self.recipe_repository.create(recipe_data, user_id)
            logger.info('Recipe saved successfully: %s', recipe.id)
            return recipe.id
        except Exception as exc:
            logger.error('Saving recipe failed: %s', exc)
            raise Exception(f'保存菜谱失败: {exc}')

    async def get_user_recipes(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        try:
            recipes = self.recipe_repository.get_by_user(user_id, limit, offset)
            result: List[Dict[str, Any]] = []

            for recipe in recipes:
                result.append(
                    {
                        'id': recipe.id,
                        'name': recipe.name,
                        'image': recipe.image,
                        'difficulty': recipe.difficulty,
                        'cooking_time': recipe.cooking_time,
                        'servings': recipe.servings,
                        'created_at': recipe.created_at.isoformat() if recipe.created_at else None,
                    }
                )

            logger.info('Fetched %s recipes for user %s', len(result), user_id)
            return result
        except Exception as exc:
            logger.error('Fetching user recipes failed: %s', exc)
            raise Exception(f'查询历史菜谱失败: {exc}')

    async def get_user_recipe_count(self, user_id: str) -> int:
        try:
            return self.recipe_repository.count_by_user(user_id)
        except Exception as exc:
            logger.error('Counting user recipes failed: %s', exc)
            raise Exception(f'统计用户菜谱数量失败: {exc}')

    async def get_recipe_by_id(self, recipe_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            recipe = self.recipe_repository.get_by_id(recipe_id)
            if not recipe or recipe.user_id != user_id:
                return None

            return {
                'id': recipe.id,
                'name': recipe.name,
                'image': recipe.image,
                'ingredients': recipe.ingredients,
                'steps': recipe.steps,
                'difficulty': recipe.difficulty,
                'cooking_time': recipe.cooking_time,
                'servings': recipe.servings,
                'safety_tips': recipe.safety_tips,
                'created_at': recipe.created_at.isoformat() if recipe.created_at else None,
            }
        except Exception as exc:
            logger.error('Fetching recipe detail failed: %s', exc)
            raise Exception(f'查询菜谱失败: {exc}')

    async def delete_recipe(self, recipe_id: str, user_id: str) -> bool:
        try:
            recipe = self.recipe_repository.get_by_id(recipe_id)
            if not recipe or recipe.user_id != user_id:
                return False
            return self.recipe_repository.delete(recipe_id)
        except Exception as exc:
            logger.error('Deleting recipe failed: %s', exc)
            raise Exception(f'删除菜谱失败: {exc}')

    async def search_recipes_by_ingredients(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        try:
            all_recipes = self.recipe_repository.get_all_recipes(limit=100)
            matched_recipes: List[Dict[str, Any]] = []
            normalized_search_terms = [item.strip().lower() for item in ingredients if item.strip()]

            for recipe in all_recipes:
                recipe_ingredients: List[str] = []
                ingredient_data = recipe.ingredients or {}

                if isinstance(ingredient_data, dict):
                    for group_name in ('main', 'secondary'):
                        for item in ingredient_data.get(group_name, []):
                            if isinstance(item, dict):
                                name = str(item.get('name', '')).strip()
                            else:
                                name = str(item).strip()
                            if name:
                                recipe_ingredients.append(name.lower())

                matched_terms = [
                    term for term in normalized_search_terms
                    if any(term in recipe_ingredient or recipe_ingredient in term for recipe_ingredient in recipe_ingredients)
                ]

                if not matched_terms:
                    continue

                match_score = int((len(matched_terms) / max(len(normalized_search_terms), 1)) * 100)
                matched_recipes.append(
                    {
                        'id': recipe.id,
                        'name': recipe.name,
                        'difficulty': recipe.difficulty,
                        'cooking_time': recipe.cooking_time,
                        'servings': recipe.servings,
                        'matchedIngredients': matched_terms,
                        'matchScore': match_score,
                    }
                )

            matched_recipes.sort(key=lambda item: item['matchScore'], reverse=True)
            return matched_recipes[:20]
        except Exception as exc:
            logger.error('Searching recipes by ingredients failed: %s', exc)
            return []
