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
        self.api_key = api_key or settings.LLM_API_KEY
        self.base_url = base_url or settings.LLM_API_BASE_URL
        self.max_retries = settings.API_MAX_RETRIES
        self.model = settings.MODEL_NAME
        self.client = httpx.AsyncClient(timeout=settings.API_TIMEOUT)
    
    def _build_recipe_prompt(
        self,
        ingredients: List[str],
        flavor_tags: List[str],
        cuisine_types: List[str],
        special_groups: List[str],
        recipe_name: Optional[str] = None
    ) -> str:
        """
        构建菜谱生成的提示词
        
        Args:
            ingredients: 食材列表
            flavor_tags: 口味标签列表
            cuisine_types: 菜系类型列表
            special_groups: 特殊人群列表
            recipe_name: 指定的菜谱名称
            
        Returns:
            str: 构建好的提示词
        """
        prompt_parts = [
            "请根据以下信息生成一个详细的菜谱：\n"
        ]
        
        # 如果指定了菜谱名称，优先使用
        if recipe_name:
            prompt_parts.append(f"菜谱名称：{recipe_name}（请严格按照这个名称生成对应的菜谱）")
        
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
        prompt_parts.append(f"- name: 菜谱名称" + (f"（必须是：{recipe_name}）" if recipe_name else ""))
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
        special_groups: List[str],
        recipe_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        调用豆包API生成菜谱
        
        Args:
            ingredients: 食材列表
            flavor_tags: 口味标签列表
            cuisine_types: 菜系类型列表
            special_groups: 特殊人群列表
            recipe_name: 指定的菜谱名称
            
        Returns:
            Dict[str, Any]: 生成的菜谱数据
            
        Raises:
            Exception: API调用失败
        """
        prompt = self._build_recipe_prompt(ingredients, flavor_tags, cuisine_types, special_groups, recipe_name)
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
        回答烹饪相关问题（非流式）
        
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
                logger.info(f"调用AI API回答烹饪问题 (尝试 {attempt + 1}/{self.max_retries + 1})")
                logger.info(f"API URL: {self.base_url}/chat/completions")
                logger.info(f"API Key (前8位): {self.api_key[:8] if self.api_key else 'None'}...")
                logger.info(f"Model: {self.model}")
                logger.info(f"问题: {question}")
                
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    json=request_body,
                    headers=headers,
                    timeout=60.0  # 增加超时时间
                )
                
                logger.info(f"API响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    logger.info(f"API响应数据结构: {list(response_data.keys())}")
                    
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        answer = response_data["choices"][0]["message"]["content"]
                        logger.info(f"✅ 成功回答烹饪问题，答案长度: {len(answer)}")
                        return answer
                    else:
                        error_msg = f"响应格式不正确，缺少choices字段。响应: {response_data}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                else:
                    error_msg = f"API返回错误状态码: {response.status_code}"
                    logger.error(f"{error_msg}, 响应: {response.text}")
                    last_error = Exception(error_msg)
                    
            except httpx.TimeoutException as e:
                logger.error(f"❌ API请求超时: {e}")
                last_error = Exception("AI服务响应超时，请稍后重试")
            except Exception as e:
                logger.error(f"❌ API调用失败: {e.__class__.__name__} - {e}", exc_info=True)
                last_error = e
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.max_retries:
                logger.warning(f"重试中，等待1秒...")
                await asyncio.sleep(1)
        
        # 所有重试都失败，抛出异常而不是返回备用答案
        logger.error(f"❌ AI服务调用失败，所有重试都失败。最后错误: {last_error}")
        raise last_error or Exception("AI服务调用失败")
    
    async def answer_cooking_question_stream(self, question: str):
        """
        回答烹饪相关问题（流式输出）
        
        Args:
            question: 用户的烹饪问题
            
        Yields:
            str: AI回答的文本片段
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
            "max_tokens": 2000,  # 增加最大token数
            "stream": True  # 启用流式输出
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"调用AI API回答烹饪问题（流式）")
        logger.info(f"API URL: {self.base_url}/chat/completions")
        logger.info(f"问题: {question}")
        logger.info(f"最大tokens: {request_body['max_tokens']}")
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=request_body,
                headers=headers,
                timeout=60.0
            ) as response:
                if response.status_code != 200:
                    error_msg = f"API返回错误状态码: {response.status_code}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                logger.info("开始接收流式响应")
                
                total_content = ""
                chunk_count = 0
                
                async for line in response.aiter_lines():
                    if not line or line.strip() == "":
                        continue
                    
                    # 记录原始行（用于调试）
                    logger.debug(f"收到行: {line[:100]}...")  # 只记录前100个字符
                    
                    # 移除 "data: " 前缀
                    if line.startswith("data: "):
                        line = line[6:]
                    
                    # 检查是否是结束标记
                    if line.strip() == "[DONE]":
                        logger.info(f"收到结束标记 [DONE]，总共接收 {chunk_count} 个块，{len(total_content)} 个字符")
                        break
                    
                    try:
                        # 解析JSON
                        chunk = json.loads(line)
                        
                        # 检查是否有finish_reason
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            choice = chunk["choices"][0]
                            finish_reason = choice.get("finish_reason")
                            
                            # 如果有finish_reason且不为null，说明流结束了
                            if finish_reason is not None:
                                logger.info(f"流结束，原因: {finish_reason}，总共 {chunk_count} 个块，{len(total_content)} 个字符")
                                break
                            
                            # 提取内容
                            delta = choice.get("delta", {})
                            content = delta.get("content", "")
                            
                            if content:
                                chunk_count += 1
                                total_content += content
                                yield content
                                
                    except json.JSONDecodeError as e:
                        logger.warning(f"解析流式响应失败: {e}, 行内容: {line[:200]}")
                        continue
                
                logger.info(f"✅ 流式响应完成，总共输出 {len(total_content)} 个字符")
                
        except Exception as e:
            logger.error(f"❌ 流式API调用失败: {e.__class__.__name__} - {e}", exc_info=True)
            raise
    
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

    async def parse_dish_ingredients(self, dish_name: str) -> Dict[str, Any]:
        """
        解析菜谱所需食材
        
        Args:
            dish_name: 菜谱名称
            
        Returns:
            Dict[str, Any]: 菜谱信息
        """
        # 构建提示词
        prompt = f"""请分析菜谱"{dish_name}"，提供以下信息：

1. 所需的主要食材（5-8种）
2. 简短的菜谱描述（一句话）

请以JSON格式返回，包含以下字段：
- name: 菜谱名称
- description: 简短描述
- ingredients: 食材数组（只包含食材名称，不包含用量）

示例：
{{
  "name": "红烧排骨",
  "description": "色泽红亮，肉质酥烂，咸甜适中的经典家常菜",
  "ingredients": ["排骨", "生姜", "大葱", "八角", "料酒", "酱油", "冰糖"]
}}"""
        
        request_body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的烹饪顾问，擅长分析菜谱和食材。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 800,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"解析菜谱: {dish_name}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=request_body,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    content = response_data["choices"][0]["message"]["content"]
                    
                    # 尝试解析JSON
                    try:
                        # 查找JSON部分
                        json_start = content.find("{")
                        json_end = content.rfind("}") + 1
                        
                        if json_start >= 0 and json_end > json_start:
                            json_str = content[json_start:json_end]
                            dish_info = json.loads(json_str)
                            logger.info(f"成功解析菜谱: {dish_name}")
                            return dish_info
                    except json.JSONDecodeError:
                        logger.warning("无法解析JSON，返回默认信息")
                    
                    # 如果解析失败，返回默认信息
                    return {
                        "name": dish_name,
                        "description": f"一道美味的{dish_name}",
                        "ingredients": ["请根据实际情况准备食材"]
                    }
            
            raise Exception(f"API返回错误状态码: {response.status_code}")
            
        except Exception as e:
            logger.error(f"解析菜谱失败: {e}")
            # 返回默认信息
            return {
                "name": dish_name,
                "description": f"一道美味的{dish_name}",
                "ingredients": ["请根据实际情况准备食材"]
            }

    async def get_ingredient_recommendation(self, ingredients: List[str]) -> Dict[str, Any]:
        """
        根据已有食材获取AI推荐
        
        Args:
            ingredients: 已有食材列表
            
        Returns:
            Dict[str, Any]: 推荐信息
        """
        # 构建提示词
        ingredients_str = "、".join(ingredients)
        prompt = f"""我现在有这些食材：{ingredients_str}

请帮我分析并提供以下建议：
1. 建议添加的食材（3-5种，能与现有食材搭配的）
2. 推荐的菜谱名称（3-5个）
3. 营养搭配建议（一句话）

请以JSON格式返回，包含以下字段：
- suggestedIngredients: 建议添加的食材数组
- recommendedDishes: 推荐的菜谱名称数组
- nutritionTips: 营养建议字符串"""
        
        request_body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的烹饪顾问，擅长食材搭配和营养分析。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"获取食材推荐: {ingredients}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=request_body,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    content = response_data["choices"][0]["message"]["content"]
                    
                    # 尝试解析JSON
                    try:
                        # 查找JSON部分
                        json_start = content.find("{")
                        json_end = content.rfind("}") + 1
                        
                        if json_start >= 0 and json_end > json_start:
                            json_str = content[json_start:json_end]
                            recommendation = json.loads(json_str)
                            logger.info(f"成功获取推荐")
                            return recommendation
                    except json.JSONDecodeError:
                        logger.warning("无法解析JSON，返回默认推荐")
                    
                    # 如果解析失败，返回默认推荐
                    return {
                        "suggestedIngredients": ["盐", "油", "酱油", "葱", "姜"],
                        "recommendedDishes": ["家常炒菜", "清炒时蔬", "简单快手菜"],
                        "nutritionTips": "建议搭配蔬菜和蛋白质，营养更均衡。"
                    }
            
            raise Exception(f"API返回错误状态码: {response.status_code}")
            
        except Exception as e:
            logger.error(f"获取推荐失败: {e}")
            # 返回默认推荐
            return {
                "suggestedIngredients": ["盐", "油", "酱油", "葱", "姜"],
                "recommendedDishes": ["家常炒菜", "清炒时蔬", "简单快手菜"],
                "nutritionTips": "建议搭配蔬菜和蛋白质，营养更均衡。"
            }
