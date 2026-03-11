"""
菜谱业务逻辑服务
"""
from typing import List, Dict, Any, Optional
import logging

from app.services.ai_service import AIService
from app.repositories.recipe_repository import RecipeRepository

logger = logging.getLogger(__name__)


class RecipeService:
    """处理菜谱相关的业务逻辑"""
    
    # 特殊人群安全提示模板
    SAFETY_TIPS = {
        "小孩": [
            "注意食材切成小块，避免噎食风险",
            "控制调味料用量，避免过咸过辣",
            "确保食材充分煮熟，避免细菌感染",
            "注意食物温度，避免烫伤"
        ],
        "老人": [
            "食材应切碎或煮软，便于咀嚼和消化",
            "控制盐分摄入，注意心血管健康",
            "避免过于油腻的食物",
            "注意食材新鲜度，避免肠胃不适"
        ],
        "孕妇": [
            "避免生食和半生食材",
            "注意食材卫生，彻底清洗",
            "避免高汞鱼类和未经巴氏消毒的奶制品",
            "控制咖啡因摄入",
            "确保营养均衡，补充叶酸"
        ],
        "糖尿病患者": [
            "控制碳水化合物摄入量",
            "避免添加过多糖分",
            "选择低GI食材",
            "注意餐后血糖监测"
        ],
        "高血压患者": [
            "严格控制盐分摄入",
            "避免腌制和加工食品",
            "多摄入富含钾的食材",
            "控制油脂摄入"
        ]
    }
    
    def __init__(
        self,
        ai_service: AIService,
        recipe_repository: RecipeRepository
    ):
        self.ai_service = ai_service
        self.recipe_repository = recipe_repository
    
    def _validate_generate_params(
        self,
        ingredients: List[str],
        recognized_ingredients: Optional[List[str]] = None
    ) -> tuple[bool, Optional[str]]:
        """
        验证生成菜谱的参数
        
        Args:
            ingredients: 用户输入的食材列表
            recognized_ingredients: 图片识别的食材列表
            
        Returns:
            tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        # 至少需要有一个食材来源
        has_ingredients = ingredients and len(ingredients) > 0
        has_recognized = recognized_ingredients and len(recognized_ingredients) > 0
        
        if not has_ingredients and not has_recognized:
            return False, "请至少提供一个食材或上传食材图片"
        
        # 验证食材不为空字符串
        all_ingredients = (ingredients or []) + (recognized_ingredients or [])
        for ing in all_ingredients:
            if not ing or not ing.strip():
                return False, "食材名称不能为空"
        
        return True, None
    
    def _add_safety_tips(
        self,
        recipe_data: Dict[str, Any],
        special_groups: List[str]
    ) -> Dict[str, Any]:
        """
        根据特殊人群添加安全提示
        
        Args:
            recipe_data: 菜谱数据
            special_groups: 特殊人群列表
            
        Returns:
            Dict[str, Any]: 添加了安全提示的菜谱数据
        """
        if not special_groups:
            return recipe_data
        
        # 收集所有相关的安全提示
        safety_tips = []
        for group in special_groups:
            if group in self.SAFETY_TIPS:
                tips = self.SAFETY_TIPS[group]
                # 添加分组标题
                safety_tips.append(f"【{group}注意事项】")
                safety_tips.extend(tips)
        
        # 如果AI已经生成了安全提示，合并它们
        if "safety_tips" in recipe_data and recipe_data["safety_tips"]:
            existing_tips = recipe_data["safety_tips"]
            if isinstance(existing_tips, list):
                safety_tips.extend(existing_tips)
        
        recipe_data["safety_tips"] = safety_tips if safety_tips else None
        return recipe_data
    
    async def generate_recipe(
        self,
        ingredients: List[str],
        flavor_tags: List[str],
        cuisine_types: List[str],
        special_groups: List[str],
        recognized_ingredients: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        生成菜谱的完整流程
        
        Args:
            ingredients: 用户输入的食材列表
            flavor_tags: 口味标签列表
            cuisine_types: 菜系类型列表
            special_groups: 特殊人群列表
            recognized_ingredients: 图片识别的食材列表
            
        Returns:
            Dict[str, Any]: 生成的菜谱数据
            
        Raises:
            ValueError: 参数验证失败
            Exception: AI服务调用失败
        """
        # 1. 验证输入参数
        is_valid, error_msg = self._validate_generate_params(ingredients, recognized_ingredients)
        if not is_valid:
            logger.warning(f"参数验证失败: {error_msg}")
            raise ValueError(error_msg)
        
        # 2. 合并所有食材
        all_ingredients = list(set((ingredients or []) + (recognized_ingredients or [])))
        logger.info(f"生成菜谱 - 食材: {all_ingredients}, 口味: {flavor_tags}, 菜系: {cuisine_types}")
        
        # 3. 调用AI服务生成菜谱
        try:
            recipe_data = await self.ai_service.generate_recipe(
                ingredients=all_ingredients,
                flavor_tags=flavor_tags,
                cuisine_types=cuisine_types,
                special_groups=special_groups
            )
        except Exception as e:
            logger.error(f"AI生成菜谱失败: {e}")
            raise Exception(f"生成菜谱失败: {str(e)}")
        
        # 4. 添加特殊人群安全提示
        recipe_data = self._add_safety_tips(recipe_data, special_groups)
        
        logger.info(f"菜谱生成成功: {recipe_data.get('name')}")
        return recipe_data
    
    async def save_recipe(
        self,
        recipe_data: Dict[str, Any],
        user_id: str
    ) -> str:
        """
        保存菜谱到数据库
        
        Args:
            recipe_data: 菜谱数据
            user_id: 用户ID
            
        Returns:
            str: 保存的菜谱ID
            
        Raises:
            Exception: 数据库操作失败
        """
        try:
            recipe = self.recipe_repository.create(recipe_data, user_id)
            logger.info(f"菜谱保存成功: {recipe.id}")
            return recipe.id
        except Exception as e:
            logger.error(f"保存菜谱失败: {e}")
            raise Exception(f"保存菜谱失败: {str(e)}")
    
    async def get_user_recipes(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取用户的历史菜谱
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            offset: 分页偏移量
            
        Returns:
            List[Dict[str, Any]]: 菜谱列表
        """
        try:
            recipes = self.recipe_repository.get_by_user(user_id, limit, offset)
            
            # 转换为字典格式
            recipe_list = []
            for recipe in recipes:
                recipe_dict = {
                    "id": recipe.id,
                    "name": recipe.name,
                    "image": recipe.image,
                    "difficulty": recipe.difficulty,
                    "cooking_time": recipe.cooking_time,
                    "servings": recipe.servings,
                    "created_at": recipe.created_at.isoformat() if recipe.created_at else None
                }
                recipe_list.append(recipe_dict)
            
            logger.info(f"查询用户菜谱: {user_id}, 数量: {len(recipe_list)}")
            return recipe_list
            
        except Exception as e:
            logger.error(f"查询用户菜谱失败: {e}")
            raise Exception(f"查询历史菜谱失败: {str(e)}")
    
    async def get_recipe_by_id(
        self,
        recipe_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        根据ID获取菜谱，验证用户权限
        
        Args:
            recipe_id: 菜谱ID
            user_id: 用户ID
            
        Returns:
            Optional[Dict[str, Any]]: 菜谱详情，不存在或无权限返回None
        """
        try:
            recipe = self.recipe_repository.get_by_id(recipe_id)
            
            if not recipe:
                logger.warning(f"菜谱不存在: {recipe_id}")
                return None
            
            # 验证用户权限
            if recipe.user_id != user_id:
                logger.warning(f"用户 {user_id} 无权访问菜谱 {recipe_id}")
                return None
            
            # 转换为字典格式
            recipe_dict = {
                "id": recipe.id,
                "name": recipe.name,
                "image": recipe.image,
                "ingredients": recipe.ingredients,
                "steps": recipe.steps,
                "difficulty": recipe.difficulty,
                "cooking_time": recipe.cooking_time,
                "servings": recipe.servings,
                "safety_tips": recipe.safety_tips,
                "created_at": recipe.created_at.isoformat() if recipe.created_at else None
            }
            
            logger.info(f"查询菜谱详情: {recipe_id}")
            return recipe_dict
            
        except Exception as e:
            logger.error(f"查询菜谱详情失败: {e}")
            raise Exception(f"查询菜谱失败: {str(e)}")
    
    async def delete_recipe(
        self,
        recipe_id: str,
        user_id: str
    ) -> bool:
        """
        删除菜谱（验证用户权限）
        
        Args:
            recipe_id: 菜谱ID
            user_id: 用户ID
            
        Returns:
            bool: 删除成功返回True
        """
        try:
            # 先查询菜谱验证权限
            recipe = self.recipe_repository.get_by_id(recipe_id)
            
            if not recipe:
                logger.warning(f"菜谱不存在: {recipe_id}")
                return False
            
            if recipe.user_id != user_id:
                logger.warning(f"用户 {user_id} 无权删除菜谱 {recipe_id}")
                return False
            
            # 删除菜谱
            success = self.recipe_repository.delete(recipe_id)
            return success
            
        except Exception as e:
            logger.error(f"删除菜谱失败: {e}")
            raise Exception(f"删除菜谱失败: {str(e)}")

    
    async def search_recipes_by_ingredients(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        """
        根据食材搜索菜谱
        
        Args:
            ingredients: 食材列表
            
        Returns:
            List[Dict[str, Any]]: 匹配的菜谱列表
        """
        try:
            # 从数据库获取所有菜谱
            all_recipes = self.recipe_repository.get_all_recipes(limit=100)
            
            # 计算匹配度
            matched_recipes = []
            
            for recipe in all_recipes:
                # 提取菜谱中的食材
                recipe_ingredients = []
                if recipe.ingredients:
                    import json
                    try:
                        ingredients_data = json.loads(recipe.ingredients) if isinstance(recipe.ingredients, str) else recipe.ingredients
                        
                        # 提取主料和配料
                        if isinstance(ingredients_data, dict):
                            main_ingredients = ingredients_data.get('main', [])
                            secondary_ingredients = ingredients_data.get('secondary', [])
                            
                            for ing in main_ingredients:
                                if isinstance(ing, dict):
                                    recipe_ingredients.append(ing.get('name', ''))
                                else:
                                    recipe_ingredients.append(str(ing))
                            
                            for ing in secondary_ingredients:
                                if isinstance(ing, dict):
                                    recipe_ingredients.append(ing.get('name', ''))
                                else:
                                    recipe_ingredients.append(str(ing))
                    except:
                        pass
                
                # 计算匹配的食材
                matched_ingredients = []
                for search_ing in ingredients:
                    for recipe_ing in recipe_ingredients:
                        if search_ing in recipe_ing or recipe_ing in search_ing:
                            matched_ingredients.append(search_ing)
                            break
                
                # 如果有匹配的食材，添加到结果
                if matched_ingredients:
                    match_score = int((len(matched_ingredients) / len(ingredients)) * 100)
                    
                    matched_recipes.append({
                        'id': recipe.id,
                        'name': recipe.name,
                        'difficulty': recipe.difficulty,
                        'cooking_time': recipe.cooking_time,
                        'servings': recipe.servings,
                        'matchedIngredients': matched_ingredients,
                        'matchScore': match_score
                    })
            
            # 按匹配度排序
            matched_recipes.sort(key=lambda x: x['matchScore'], reverse=True)
            
            return matched_recipes[:20]  # 返回前20个结果
            
        except Exception as e:
            logger.error(f"搜索菜谱失败: {e}")
            return []
