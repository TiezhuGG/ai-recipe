"""
菜谱相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class Ingredient(BaseModel):
    """食材模型"""
    name: str
    amount: str
    unit: str


class RecipeIngredients(BaseModel):
    """菜谱食材模型"""
    main: List[Ingredient]
    secondary: List[Ingredient]


class RecipeStep(BaseModel):
    """烹饪步骤模型"""
    order: int
    description: str
    image: Optional[str] = None


class GenerateRecipeRequest(BaseModel):
    """生成菜谱请求模型"""
    ingredients: List[str] = Field(default_factory=list, description="食材列表")
    flavor_tags: List[str] = Field(default_factory=list, description="口味标签")
    cuisine_types: List[str] = Field(default_factory=list, description="菜系类型")
    special_groups: List[str] = Field(default_factory=list, description="特殊人群")
    recognized_ingredients: Optional[List[str]] = Field(None, description="图片识别的食材")


class RecipeResponse(BaseModel):
    """菜谱响应模型"""
    id: Optional[str] = None
    name: str
    image: Optional[str] = None
    ingredients: RecipeIngredients
    steps: List[RecipeStep]
    difficulty: Literal["easy", "medium", "hard"]
    cooking_time: int = Field(description="烹饪时间（分钟）")
    servings: int = Field(description="建议人数")
    safety_tips: Optional[List[str]] = None
    created_at: Optional[str] = None


class SaveRecipeRequest(BaseModel):
    """保存菜谱请求模型"""
    name: str
    image: Optional[str] = None
    ingredients: dict
    steps: List[dict]
    difficulty: str
    cooking_time: int
    servings: int
    safety_tips: Optional[List[str]] = None


class SaveRecipeResponse(BaseModel):
    """保存菜谱响应模型"""
    id: str
    success: bool
    message: str = "菜谱保存成功"


class RecipeListItem(BaseModel):
    """菜谱列表项模型"""
    id: str
    name: str
    image: Optional[str] = None
    difficulty: str
    cooking_time: int
    servings: int
    created_at: Optional[str] = None


class RecipeHistoryResponse(BaseModel):
    """历史菜谱响应模型"""
    recipes: List[RecipeListItem]
    total: int
    limit: int
    offset: int


class ImageRecognitionResponse(BaseModel):
    """图片识别响应模型"""
    ingredients: List[str]
    confidence: float = 0.8
    message: str = "识别成功"


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str
    detail: Optional[str] = None
