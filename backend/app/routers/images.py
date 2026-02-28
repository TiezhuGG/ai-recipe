"""
图片相关路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import logging

from app.schemas.recipe_schemas import ImageRecognitionResponse
from app.services.image_service import ImageService
from app.services.ai_service import AIService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_image_service() -> ImageService:
    """获取ImageService实例"""
    return ImageService()


def get_ai_service() -> AIService:
    """获取AIService实例"""
    return AIService()


@router.post("/images/recognize", response_model=ImageRecognitionResponse)
async def recognize_ingredients(
    file: UploadFile = File(...),
    image_service: ImageService = Depends(get_image_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """
    上传图片并识别食材
    
    Args:
        file: 上传的图片文件
        
    Returns:
        ImageRecognitionResponse: 识别的食材列表
        
    Raises:
        400: 文件格式不支持或文件过大
        500: AI识别服务失败
    """
    try:
        # 1. 保存上传的图片
        try:
            file_path = await image_service.save_uploaded_image(file)
            logger.info(f"图片保存成功: {file_path}")
        except ValueError as e:
            # 文件验证失败
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"保存图片失败: {e}")
            raise HTTPException(status_code=500, detail="保存图片失败")
        
        # 2. 调用AI服务识别食材
        try:
            ingredients = await ai_service.recognize_ingredients(file_path)
            logger.info(f"识别到食材: {ingredients}")
            
            return ImageRecognitionResponse(
                ingredients=ingredients,
                confidence=0.8,
                message="识别成功"
            )
            
        except Exception as e:
            logger.error(f"识别食材失败: {e}")
            # 识别失败，删除已保存的图片
            image_service.delete_image(file_path)
            raise HTTPException(status_code=500, detail=f"识别食材失败: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理图片识别请求失败: {e}")
        raise HTTPException(status_code=500, detail="处理请求失败")
