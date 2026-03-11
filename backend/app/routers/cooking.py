"""
烹饪学习相关路由
"""
from fastapi import APIRouter, Depends, HTTPException
import logging

from app.services.ai_service import AIService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_ai_service() -> AIService:
    """获取AIService实例"""
    return AIService()


@router.post("/cooking/ask")
async def ask_cooking_question(
    request: dict,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    询问烹饪问题（AI对话）
    
    Args:
        request: 包含question的请求体
        
    Returns:
        dict: 包含answer的响应
    """
    try:
        question = request.get('question', '')
        
        if not question:
            raise HTTPException(status_code=400, detail="问题不能为空")
        
        logger.info(f"收到烹饪问题: {question}")
        
        # 调用AI服务回答问题
        answer = await ai_service.answer_cooking_question(question)
        
        logger.info(f"成功回答问题，答案长度: {len(answer)}")
        
        return {
            "success": True,
            "answer": answer
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"回答烹饪问题失败: {e.__class__.__name__} - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI服务调用失败: {str(e)}")


@router.post("/cooking/diagnose")
async def diagnose_cooking_problem(
    request: dict,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    诊断烹饪问题
    
    Args:
        request: 包含problem的请求体
        
    Returns:
        dict: 包含diagnosis的响应
    """
    try:
        problem = request.get('problem', '')
        
        if not problem:
            raise HTTPException(status_code=400, detail="问题描述不能为空")
        
        logger.info(f"收到烹饪问题诊断请求: {problem}")
        
        # 调用AI服务诊断问题
        diagnosis = await ai_service.diagnose_cooking_problem(problem)
        
        logger.info(f"成功诊断问题，诊断结果长度: {len(diagnosis)}")
        
        return {
            "success": True,
            "diagnosis": diagnosis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"诊断烹饪问题失败: {e.__class__.__name__} - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI服务调用失败: {str(e)}")
