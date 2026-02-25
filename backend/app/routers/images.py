"""
图片相关路由
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/images/recognize")
async def recognize_ingredients():
    """图片识别端点（待实现）"""
    return {"message": "图片识别功能待实现"}
