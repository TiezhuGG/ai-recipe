"""
AI服务 - 与豆包API交互
"""
from typing import List, Dict, Any, Optional
import httpx
import json
import logging
import asyncio
import base64

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """处理与豆包API的交互"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or settings.DOUBAO_API_KEY
        self.base_url = base_url or settings.DOUBAO_API_BASE_URL
        self.max_retries = settings.API_MAX_RETRIES
        self.model = settings.MODEL_NAME
        self.client = httpx.AsyncClient(timeout=settings.API_TIMEOUT)
    
    def _build_recipe_prompt(
        self,
        ingredients: List[str],
        flavor_tags: List[str],
        cuisine_types: List[str],
        special_groups: List[str]
    ) -> str:
        """
        构建菜谱生成的提示词
        
        Args:
            ingredients: 食材列表
            flavor_tags: 口味标签列表
            cuisine_types: 菜系类型列表
            special_groups: 特殊人群列表
            
        Returns:
            str: 构建好的提示词
        """
        prompt_parts = [
            "请根据以下信息生成一个详细的菜谱：\n"
        ]
        
        # 添加食材信息
        if ingredients:
            ingredients_str = "、".join(ingredients)
            prompt_parts.append(f"食材：{ingredients_str}")
        
        # 添加口味标签
        if flavor_tags:
            flavor_str = "、".join(flavor_tags)
            prompt_parts.append(f"口味偏好：{flavor_str}")
        
        # 添加菜系类型
        if cuisine_types:
            cuisine_str = "、".join(cuisine_types)
            prompt_parts.append(f"菜系：{cuisine_str}")
        
        # 添加特殊人群
        if special_groups:
            groups_str = "、".join(special_groups)
            prompt_parts.append(f"特殊人群：{groups_str}（请在安全提示中特别注意）")
        
        prompt_parts.append("\n请以JSON格式返回菜谱，包含以下字段：")
        prompt_parts.append("- name: 菜谱名称")
        prompt_parts.append("- ingredients: 食材对象，包含main（主料数组）和secondary（配料数组），每个食材包含name、amount、unit")
        prompt_parts.append("- steps: 步骤数组，每个步骤包含order（序号）和description（描述）")
        prompt_parts.append("- difficulty: 难度（easy/medium/hard）")
        prompt_parts.append("- cooking_time: 烹饪时间（分钟，整数）")
        prompt_parts.append("- servings: 建议人数（整数）")
        
        if special_groups:
            prompt_parts.append("- safety_tips: 安全提示数组（针对特殊人群的饮食注意事项）")
        
        prompt = "\n".join(prompt_parts)
        logger.debug(f"构建的提示词: {prompt}")
        return prompt
    
    def _parse_recipe_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析AI返回的菜谱数据
        
        Args:
            response: AI API返回的响应
            
        Returns:
            Dict[str, Any]: 解析后的菜谱数据
            
        Raises:
            ValueError: 解析失败
        """
        try:
            # 豆包API返回格式：{"choices": [{"message": {"content": "..."}}]}
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]
                
                # 尝试解析JSON内容
                # 有时AI会在JSON前后添加说明文字，需要提取JSON部分
                content = content.strip()
                
                # 查找JSON开始和结束位置
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    recipe_data = json.loads(json_str)
                    
                    # 验证必需字段
                    required_fields = ["name", "ingredients", "steps", "difficulty", "cooking_time", "servings"]
                    for field in required_fields:
                        if field not in recipe_data:
                            raise ValueError(f"缺少必需字段: {field}")
                    
                    logger.info(f"成功解析菜谱: {recipe_data.get('name')}")
                    return recipe_data
                else:
                    raise ValueError("响应中未找到有效的JSON数据")
            else:
                raise ValueError("响应格式不正确")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            raise ValueError(f"无法解析AI返回的数据: {e}")
        except Exception as e:
            logger.error(f"解析响应失败: {e}")
            raise
    
    async def generate_recipe(
        self,
        ingredients: List[str],
        flavor_tags: List[str],
        cuisine_types: List[str],
        special_groups: List[str]
    ) -> Dict[str, Any]:
        """
        调用豆包API生成菜谱
        
        Args:
            ingredients: 食材列表
            flavor_tags: 口味标签列表
            cuisine_types: 菜系类型列表
            special_groups: 特殊人群列表
            
        Returns:
            Dict[str, Any]: 生成的菜谱数据
            
        Raises:
            Exception: API调用失败
        """
        prompt = self._build_recipe_prompt(ingredients, flavor_tags, cuisine_types, special_groups)
        # 构建请求体（豆包API格式）
        request_body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的烹饪助手，擅长根据食材和用户偏好生成详细的菜谱。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False,
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 实现重试机制
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"调用豆包API生成菜谱 (尝试 {attempt + 1}/{self.max_retries + 1})")
                
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    json=request_body,
                    headers=headers
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    recipe_data = self._parse_recipe_response(response_data)
                    return recipe_data
                else:
                    error_msg = f"API返回错误状态码: {response.status_code}"
                    logger.error(f"{error_msg}, 响应: {response.text}")
                    last_error = Exception(error_msg)
                    
            except httpx.TimeoutException as e:
                logger.error(f"API请求超时: {e}")
                last_error = Exception("AI服务响应超时，请稍后重试")
            except httpx.RequestError as e:
                logger.error(f"API请求失败: {e.__class__.__name__} - {e}")
                last_error = e
            except Exception as e:
                logger.error(f"API调用中发生未知错误: {e.__class__.__name__} - {e}", exc_info=True)
                last_error = e
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.max_retries:
                await asyncio.sleep(1)
        
        # 所有重试都失败
        raise last_error or Exception("AI服务调用失败")
    
    async def recognize_ingredients(self, image_path: str) -> List[str]:
        """
        调用豆包API识别图片中的食材
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            List[str]: 识别的食材列表
            
        Raises:
            Exception: API调用失败
        """
        # 读取图片文件
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            logger.error(f"读取图片文件失败: {e}")
            raise Exception("无法读取图片文件")
        
        # 构建请求（豆包视觉API格式）
        # 注意：这里需要根据豆包实际的图像识别API格式调整
        prompt = "请识别图片中的食材，只返回食材名称列表，用逗号分隔。"
        
        request_body = {
            "model": self.model,  # 视觉模型ID
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.3
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 实现重试机制
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"调用豆包API识别食材 (尝试 {attempt + 1}/{self.max_retries + 1})")
                
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    json=request_body,
                    headers=headers
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # 解析识别结果
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        content = response_data["choices"][0]["message"]["content"]
                        # 解析逗号分隔的食材列表
                        ingredients = [ing.strip() for ing in content.split(",") if ing.strip()]
                        logger.info(f"识别到食材: {ingredients}")
                        return ingredients
                    else:
                        raise ValueError("响应格式不正确")
                else:
                    error_msg = f"API返回错误状态码: {response.status_code}"
                    logger.error(f"{error_msg}, 响应: {response.text}")
                    last_error = Exception(error_msg)
                    
            except httpx.TimeoutException as e:
                logger.error(f"API请求超时: {e}")
                last_error = Exception("图片识别服务响应超时，请稍后重试")
            except Exception as e:
                logger.error(f"API调用失败: {e}")
                last_error = e
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.max_retries:
                await asyncio.sleep(1)
        
        # 所有重试都失败
        raise last_error or Exception("图片识别服务调用失败")
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
    
    async def generate_dish_image(self, recipe_name: str, ingredients: List[str]) -> str:
        """
        调用豆包API生成菜品效果图
        
        Args:
            recipe_name: 菜谱名称
            ingredients: 食材列表
            
        Returns:
            str: 生成的图片URL或base64数据
            
        Raises:
            Exception: API调用失败
        """
        # 构建图片生成提示词
        ingredients_str = "、".join(ingredients[:5])  # 只取前5个主要食材
        prompt = f"一道精美的{recipe_name}，主要食材包括{ingredients_str}，摆盘精致，色彩鲜艳，专业美食摄影风格，高清画质"
        
        logger.info(f"生成菜品图片提示词: {prompt}")
        
        # 临时方案：使用占位图服务
        # TODO: 当豆包图像生成API可用时，替换为真实的API调用
        try:
            # 方案1: 尝试调用豆包图像生成API
            request_body = {
                "model": "doubao-image-generation",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "standard",
                "style": "vivid"
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            try:
                response = await self.client.post(
                    f"{self.base_url}/images/generations",
                    json=request_body,
                    headers=headers,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    if "data" in response_data and len(response_data["data"]) > 0:
                        image_url = response_data["data"][0].get("url")
                        if image_url:
                            logger.info(f"成功生成菜品图片: {image_url}")
                            return image_url
            except Exception as api_error:
                logger.warning(f"豆包图像API调用失败，使用备用方案: {api_error}")
            
            # 方案2: 使用Foodish API（免费的随机美食图片API）
            try:
                # Foodish API 提供真实的美食图片
                foodish_response = await self.client.get(
                    "https://foodish-api.com/api/",
                    timeout=10.0
                )
                if foodish_response.status_code == 200:
                    foodish_data = foodish_response.json()
                    if "image" in foodish_data:
                        logger.info(f"使用Foodish美食图片: {foodish_data['image']}")
                        return foodish_data["image"]
            except Exception as foodish_error:
                logger.warning(f"Foodish API调用失败: {foodish_error}")
            
            # 方案3: 使用Unsplash美食图片（需要关键词匹配）
            try:
                # 提取食材关键词用于搜索
                if ingredients:
                    # 使用第一个食材作为关键词
                    keyword = ingredients[0]
                else:
                    keyword = "food"
                
                # Unsplash Source API（不需要API key）
                unsplash_url = f"https://source.unsplash.com/800x600/?food,{keyword},dish"
                logger.info(f"使用Unsplash美食图片: {unsplash_url}")
                return unsplash_url
            except Exception as unsplash_error:
                logger.warning(f"Unsplash API调用失败: {unsplash_error}")

            
        except Exception as e:
            logger.error(f"生成菜品图片失败: {e}")
        
        # 最终备用方案：返回一个美食主题的占位图
        # 使用绿色主题，显示菜谱名称和美食emoji
        import urllib.parse
        encoded_name = urllib.parse.quote(recipe_name)
        return f"https://via.placeholder.com/800x600/22c55e/ffffff?text={encoded_name}+%F0%9F%8D%B2"
    
    async def answer_cooking_question(self, question: str) -> str:
        """
        回答烹饪相关问题
        
        Args:
            question: 用户的烹饪问题
            
        Returns:
            str: AI的回答
        """
        # 构建系统提示词
        system_prompt = """你是一位经验丰富的烹饪导师，擅长解答各种烹饪问题。
你的回答应该：
1. 专业且易懂
2. 提供具体的操作建议
3. 包含实用的技巧
4. 考虑安全和健康因素
5. 语气友好亲切"""
        
        request_body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 实现重试机制
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"调用豆包API回答烹饪问题 (尝试 {attempt + 1}/{self.max_retries + 1})")
                logger.debug(f"API URL: {self.base_url}/chat/completions")
                logger.debug(f"API Key (前8位): {self.api_key[:8]}...")
                logger.debug(f"Model: {self.model}")
                
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    json=request_body,
                    headers=headers,
                    timeout=30.0
                )
                
                logger.info(f"API响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    logger.debug(f"API响应数据: {response_data}")
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        answer = response_data["choices"][0]["message"]["content"]
                        logger.info(f"成功回答烹饪问题")
                        return answer
                    else:
                        raise ValueError("响应格式不正确")
                else:
                    error_msg = f"API返回错误状态码: {response.status_code}"
                    logger.error(f"{error_msg}, 响应: {response.text}")
                    last_error = Exception(error_msg)
                    
            except httpx.TimeoutException as e:
                logger.error(f"API请求超时: {e}")
                last_error = Exception("AI服务响应超时，请稍后重试")
            except Exception as e:
                logger.error(f"API调用失败: {e.__class__.__name__} - {e}", exc_info=True)
                last_error = e
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.max_retries:
                await asyncio.sleep(1)
        
        # 所有重试都失败，返回备用回答
        logger.warning(f"AI服务调用失败，使用备用回答。最后错误: {last_error}")
        return self._get_fallback_answer(question)
    
    async def diagnose_cooking_problem(self, problem: str) -> str:
        """
        诊断烹饪问题
        
        Args:
            problem: 问题描述
            
        Returns:
            str: 诊断结果和建议
        """
        # 构建系统提示词
        system_prompt = """你是一位专业的烹饪问题诊断专家。
根据用户描述的问题，你需要：
1. 分析可能的原因
2. 提供具体的解决方案
3. 给出预防建议
4. 语气专业但友好"""
        
        request_body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"我遇到的烹饪问题是：{problem}\n\n请帮我诊断并提供解决方案。"}
            ],
            "temperature": 0.7,
            "max_tokens": 1500,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 实现重试机制
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"调用豆包API诊断烹饪问题 (尝试 {attempt + 1}/{self.max_retries + 1})")
                logger.debug(f"API URL: {self.base_url}/chat/completions")
                logger.debug(f"API Key (前8位): {self.api_key[:8]}...")
                logger.debug(f"Model: {self.model}")
                
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    json=request_body,
                    headers=headers,
                    timeout=30.0
                )
                
                logger.info(f"API响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    logger.debug(f"API响应数据: {response_data}")
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        diagnosis = response_data["choices"][0]["message"]["content"]
                        logger.info(f"成功诊断烹饪问题")
                        return diagnosis
                    else:
                        raise ValueError("响应格式不正确")
                else:
                    error_msg = f"API返回错误状态码: {response.status_code}"
                    logger.error(f"{error_msg}, 响应: {response.text}")
                    last_error = Exception(error_msg)
                    
            except httpx.TimeoutException as e:
                logger.error(f"API请求超时: {e}")
                last_error = Exception("AI服务响应超时，请稍后重试")
            except Exception as e:
                logger.error(f"API调用失败: {e.__class__.__name__} - {e}", exc_info=True)
                last_error = e
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.max_retries:
                await asyncio.sleep(1)
        
        # 所有重试都失败，返回备用诊断
        logger.warning(f"AI服务调用失败，使用备用诊断。最后错误: {last_error}")
        return self._get_fallback_diagnosis(problem)
    
    def _get_fallback_answer(self, question: str) -> str:
        """获取备用回答"""
        fallback_answers = {
            "火候": "掌握火候的关键是：大火快炒保持食材脆嫩，中火慢炖让味道充分融合，小火慢煮保持食材完整。建议多练习，观察食材的变化。",
            "调味": "基本调味比例：盐1份、糖0.5份、醋0.3份、酱油适量。记住'咸鲜为主，酸甜为辅'的原则，可以边尝边调整。",
            "刀工": "刀工的基本原则：顺纹切肉逆纹切，保持刀具锋利，切菜时手指弯曲保护指尖。多练习基本刀法，从简单开始。",
        }
        
        for keyword, answer in fallback_answers.items():
            if keyword in question:
                return answer
        
        return "这是一个很好的问题！建议您：\n1. 多观察食材的变化\n2. 掌握基本的烹饪原理\n3. 多实践多总结\n4. 可以参考专业烹饪书籍或视频教程"
    
    def _get_fallback_diagnosis(self, problem: str) -> str:
        """获取备用诊断"""
        return f"""根据您描述的问题，可能的原因和解决方案：

**可能原因：**
1. 火候控制不当
2. 调味比例不合适
3. 烹饪时间过长或过短
4. 食材处理不到位

**解决方案：**
1. 注意观察食材的颜色和状态变化
2. 按照菜谱建议的比例调味，可以先少放后补
3. 掌握不同食材的最佳烹饪时间
4. 确保食材新鲜，处理干净

**预防建议：**
- 提前准备好所有食材和调料
- 熟悉菜谱的每个步骤
- 保持厨房整洁有序
- 多练习基本功

如果问题持续，建议观看相关的烹饪教学视频，或咨询专业厨师。"""