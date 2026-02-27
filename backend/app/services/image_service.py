"""
图片处理服务
"""
from fastapi import UploadFile
from typing import Optional
import os
import uuid
import logging
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class ImageService:
    """处理图片上传和存储"""
    
    # 支持的图片格式
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/jpg", 
        "image/png",
        "image/webp"
    }
    
    def __init__(self, upload_dir: str = None):
        self.upload_dir = upload_dir or settings.UPLOAD_DIR
        # 确保上传目录存在
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def validate_image(self, file: UploadFile) -> tuple[bool, Optional[str]]:
        """
        验证图片格式和大小
        
        Args:
            file: 上传的文件对象
            
        Returns:
            tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        # 验证文件名
        if not file.filename:
            return False, "文件名不能为空"
        
        # 验证文件扩展名
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            return False, f"不支持的文件格式。支持的格式: {', '.join(self.ALLOWED_EXTENSIONS)}"
        
        # 验证MIME类型
        if file.content_type and file.content_type not in self.ALLOWED_MIME_TYPES:
            return False, f"不支持的文件类型: {file.content_type}"
        
        # 验证文件大小（需要读取文件）
        # 注意：这会消耗文件流，需要在调用后重置
        try:
            file.file.seek(0, 2)  # 移动到文件末尾
            file_size = file.file.tell()  # 获取文件大小
            file.file.seek(0)  # 重置到文件开头
            
            if file_size > settings.MAX_UPLOAD_SIZE:
                size_mb = file_size / (1024 * 1024)
                max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
                return False, f"文件过大 ({size_mb:.2f}MB)。最大允许 {max_mb}MB"
            
            if file_size == 0:
                return False, "文件为空"
                
        except Exception as e:
            logger.error(f"验证文件大小失败: {e}")
            return False, "无法验证文件大小"
        
        return True, None
    
    def generate_filename(self, original_filename: str) -> str:
        """
        生成唯一的文件名
        
        Args:
            original_filename: 原始文件名
            
        Returns:
            str: 生成的唯一文件名
        """
        # 获取文件扩展名
        file_ext = Path(original_filename).suffix.lower()
        
        # 生成UUID作为文件名
        unique_id = str(uuid.uuid4())
        new_filename = f"{unique_id}{file_ext}"
        
        logger.debug(f"生成文件名: {original_filename} -> {new_filename}")
        return new_filename
    
    async def save_uploaded_image(self, file: UploadFile) -> str:
        """
        保存上传的图片
        
        Args:
            file: 上传的文件对象
            
        Returns:
            str: 保存的文件路径
            
        Raises:
            ValueError: 文件验证失败
            Exception: 文件保存失败
        """
        # 1. 验证文件
        is_valid, error_msg = self.validate_image(file)
        if not is_valid:
            logger.warning(f"文件验证失败: {error_msg}")
            raise ValueError(error_msg)
        
        # 2. 生成唯一文件名
        new_filename = self.generate_filename(file.filename)
        file_path = os.path.join(self.upload_dir, new_filename)
        
        # 3. 保存文件
        try:
            # 读取文件内容
            contents = await file.read()
            
            # 写入文件
            with open(file_path, "wb") as f:
                f.write(contents)
            
            logger.info(f"文件保存成功: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"保存文件失败: {e}")
            # 如果保存失败，尝试删除部分写入的文件
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            raise Exception(f"保存文件失败: {str(e)}")
        finally:
            # 确保文件流被关闭
            await file.close()
    
    def delete_image(self, file_path: str) -> bool:
        """
        删除图片文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 删除成功返回True
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"删除文件成功: {file_path}")
                return True
            else:
                logger.warning(f"文件不存在: {file_path}")
                return False
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False
    
    def get_file_url(self, file_path: str) -> str:
        """
        获取文件的访问URL
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 文件URL
        """
        # 提取文件名
        filename = os.path.basename(file_path)
        # 返回相对URL（前端可以拼接完整URL）
        return f"/uploads/{filename}"
    
    def file_exists(self, file_path: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 文件存在返回True
        """
        return os.path.exists(file_path)
