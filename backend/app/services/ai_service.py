"""AI service backed by an OpenAI-compatible API."""
from __future__ import annotations

import asyncio
import base64
import html
import json
import logging
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Wraps recipe generation and cooking assistance requests."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.base_url = (base_url or settings.LLM_BASE_URL).rstrip("/")
        self.max_retries = settings.API_MAX_RETRIES
        self.model = settings.MODEL_NAME
        self.image_model = settings.IMAGE_MODEL_NAME or ""
        self.client = httpx.AsyncClient(timeout=settings.API_TIMEOUT)

    async def close(self):
        await self.client.aclose()

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _post_json(self, path: str, payload: Dict[str, Any], timeout: float | None = None) -> Dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.post(
                    f"{self.base_url}{path}",
                    json=payload,
                    headers=self._headers(),
                    timeout=timeout or settings.API_TIMEOUT,
                )
                response.raise_for_status()
                return response.json()
            except Exception as exc:
                last_error = exc
                logger.warning("AI request failed on attempt %s/%s: %s", attempt + 1, self.max_retries + 1, exc)
                if attempt < self.max_retries:
                    await asyncio.sleep(1)
        raise last_error or RuntimeError("AI request failed")

    def _extract_content(self, response_data: Dict[str, Any]) -> str:
        try:
            return response_data["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            raise ValueError(f"Invalid AI response format: {exc}") from exc

    def _extract_json_object(self, text: str) -> Dict[str, Any]:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("No JSON object found in AI response")
        return json.loads(text[start : end + 1])

    def _wrap_base64_image(self, encoded_image: str, mime_type: str = "image/png") -> str:
        return f"data:{mime_type};base64,{encoded_image}"

    def _build_dish_image_placeholder(self, recipe_name: str, ingredients: List[str]) -> str:
        ingredient_text = " / ".join(ingredients[:5]) if ingredients else "智能菜谱效果图"
        escaped_title = html.escape(recipe_name)
        escaped_ingredients = html.escape(ingredient_text)
        svg = f'''
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1f3a5f"/>
      <stop offset="55%" stop-color="#8b4513"/>
      <stop offset="100%" stop-color="#f0b35e"/>
    </linearGradient>
    <radialGradient id="plateGlow" cx="50%" cy="45%" r="42%">
      <stop offset="0%" stop-color="#fff6d5" stop-opacity="0.95"/>
      <stop offset="70%" stop-color="#f2d59a" stop-opacity="0.92"/>
      <stop offset="100%" stop-color="#d9b16a" stop-opacity="1"/>
    </radialGradient>
  </defs>
  <rect width="1024" height="1024" fill="url(#bg)"/>
  <circle cx="512" cy="460" r="285" fill="url(#plateGlow)"/>
  <circle cx="512" cy="460" r="245" fill="#fffaf0" opacity="0.96"/>
  <ellipse cx="512" cy="470" rx="205" ry="125" fill="#8a4b24" opacity="0.18"/>
  <ellipse cx="512" cy="470" rx="175" ry="92" fill="#d08b4f" opacity="0.35"/>
  <g opacity="0.92">
    <ellipse cx="430" cy="445" rx="80" ry="26" fill="#f5f0e6"/>
    <ellipse cx="590" cy="452" rx="92" ry="28" fill="#efe6d6"/>
    <ellipse cx="505" cy="500" rx="115" ry="30" fill="#efe4d1"/>
    <circle cx="428" cy="418" r="22" fill="#8b2f22"/>
    <circle cx="478" cy="410" r="18" fill="#9f3c2e"/>
    <circle cx="554" cy="408" r="20" fill="#7b291f"/>
    <circle cx="610" cy="430" r="18" fill="#8c3527"/>
    <circle cx="465" cy="504" r="19" fill="#3f7f43"/>
    <circle cx="530" cy="518" r="16" fill="#4c8d4f"/>
    <circle cx="585" cy="494" r="17" fill="#588f49"/>
    <path d="M390 380 C470 520, 560 520, 640 385" stroke="#ebe0cd" stroke-width="14" fill="none" stroke-linecap="round" opacity="0.9"/>
    <path d="M380 410 C455 555, 575 550, 655 420" stroke="#f3eadf" stroke-width="12" fill="none" stroke-linecap="round" opacity="0.82"/>
    <path d="M405 402 C495 560, 560 548, 622 415" stroke="#e7dac6" stroke-width="10" fill="none" stroke-linecap="round" opacity="0.76"/>
  </g>
  <rect x="120" y="710" width="784" height="180" rx="28" fill="#111827" fill-opacity="0.6"/>
  <text x="512" y="785" text-anchor="middle" font-size="54" font-weight="700" fill="#fff7ed" font-family="Microsoft YaHei, PingFang SC, sans-serif">{escaped_title}</text>
  <text x="512" y="845" text-anchor="middle" font-size="30" fill="#fde7c7" font-family="Microsoft YaHei, PingFang SC, sans-serif">{escaped_ingredients}</text>
  <text x="512" y="892" text-anchor="middle" font-size="22" fill="#f6d8a8" font-family="Microsoft YaHei, PingFang SC, sans-serif">未配置专用图像模型，当前返回菜品示意图以避免错误菜图</text>
</svg>
'''.strip()
        encoded_svg = base64.b64encode(svg.encode("utf-8")).decode("ascii")
        return self._wrap_base64_image(encoded_svg, "image/svg+xml")

    def _build_recipe_prompt(
        self,
        ingredients: List[str],
        flavor_tags: List[str],
        cuisine_types: List[str],
        special_groups: List[str],
        recipe_name: Optional[str] = None,
    ) -> str:
        lines = ["请根据以下信息生成一份详细菜谱，并严格返回 JSON。"]
        if recipe_name:
            lines.append(f"菜谱名称：{recipe_name}")
        if ingredients:
            lines.append(f"食材：{', '.join(ingredients)}")
        if flavor_tags:
            lines.append(f"口味偏好：{', '.join(flavor_tags)}")
        if cuisine_types:
            lines.append(f"菜系偏好：{', '.join(cuisine_types)}")
        if special_groups:
            lines.append(f"适用人群：{', '.join(special_groups)}")

        lines.extend(
            [
                "返回字段：",
                "name: 菜名",
                "ingredients: { main: [{ name, amount, unit }], secondary: [{ name, amount, unit }] }",
                "steps: [{ order, description, image }]",
                "difficulty: easy | medium | hard",
                "cooking_time: 整数分钟",
                "servings: 整数人数",
                "safety_tips: 字符串数组，可为空",
                "不要输出 Markdown 代码块，只输出 JSON。",
            ]
        )
        return "\n".join(lines)

    async def generate_recipe(
        self,
        ingredients: List[str],
        flavor_tags: List[str],
        cuisine_types: List[str],
        special_groups: List[str],
        recipe_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一名专业中文烹饪助理，擅长根据食材和偏好输出结构化菜谱。",
                },
                {
                    "role": "user",
                    "content": self._build_recipe_prompt(
                        ingredients,
                        flavor_tags,
                        cuisine_types,
                        special_groups,
                        recipe_name,
                    ),
                },
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False,
        }
        response_data = await self._post_json("/chat/completions", payload)
        recipe_data = self._extract_json_object(self._extract_content(response_data))

        required_fields = {"name", "ingredients", "steps", "difficulty", "cooking_time", "servings"}
        missing = required_fields - set(recipe_data.keys())
        if missing:
            raise ValueError(f"Missing fields in AI recipe response: {', '.join(sorted(missing))}")
        return recipe_data

    async def recognize_ingredients(self, image_path: str) -> List[str]:
        try:
            with open(image_path, "rb") as file_obj:
                image_data = base64.b64encode(file_obj.read()).decode("utf-8")
        except Exception as exc:
            raise Exception(f"无法读取图片文件: {exc}") from exc

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请识别图片中的食材，只返回逗号分隔的食材名称。"},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                        },
                    ],
                }
            ],
            "temperature": 0.2,
            "stream": False,
        }
        response_data = await self._post_json("/chat/completions", payload)
        content = self._extract_content(response_data)
        ingredients = [item.strip() for item in content.replace("，", ",").split(",") if item.strip()]
        return ingredients

    async def generate_dish_image(self, recipe_name: str, ingredients: List[str]) -> str:
        prompt = f"一道精致的{recipe_name}成品图，主要食材包括{', '.join(ingredients[:5])}，专业美食摄影风格。"

        if self.image_model:
            payload = {
                "model": self.image_model,
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
            }
            try:
                response_data = await self._post_json("/images/generations", payload, timeout=60.0)
                data = response_data.get("data") or []
                if data:
                    image_url = data[0].get("url")
                    if image_url:
                        return image_url

                    encoded_image = data[0].get("b64_json")
                    if encoded_image:
                        return self._wrap_base64_image(encoded_image)
            except Exception as exc:
                logger.warning("Image generation request failed, using placeholder image instead: %s", exc)
        else:
            logger.info("IMAGE_MODEL_NAME is empty, using dish placeholder image for %s", recipe_name)

        return self._build_dish_image_placeholder(recipe_name, ingredients)

    async def answer_cooking_question(self, question: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位经验丰富的中文烹饪导师，请给出专业、易懂、可操作的建议。",
                },
                {"role": "user", "content": question},
            ],
            "temperature": 0.7,
            "max_tokens": 1200,
            "stream": False,
        }
        response_data = await self._post_json("/chat/completions", payload)
        return self._extract_content(response_data)

    async def answer_cooking_question_stream(self, question: str) -> AsyncIterator[str]:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位经验丰富的中文烹饪导师，请给出专业、易懂、可操作的建议。",
                },
                {"role": "user", "content": question},
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": True,
        }

        async with self.client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            json=payload,
            headers=self._headers(),
            timeout=60.0,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    line = line[6:]
                if line.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(line)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue

    async def diagnose_cooking_problem(self, problem: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业烹饪问题诊断专家，请分析原因、给出解决方案，并附上预防建议。",
                },
                {"role": "user", "content": problem},
            ],
            "temperature": 0.7,
            "max_tokens": 1500,
            "stream": False,
        }
        try:
            response_data = await self._post_json("/chat/completions", payload, timeout=30.0)
            return self._extract_content(response_data)
        except Exception as exc:
            logger.warning("Diagnose failed, using fallback answer: %s", exc)
            return self._get_fallback_diagnosis(problem)

    def _get_fallback_diagnosis(self, problem: str) -> str:
        return (
            f"根据你描述的问题“{problem}”，可以优先检查这几项：\n"
            "1. 火候是否过大或过小。\n"
            "2. 调味是否过早或比例失衡。\n"
            "3. 食材是否没有提前处理到位。\n"
            "4. 烹饪时间是否偏长或偏短。\n\n"
            "建议先从火候、盐量和下锅顺序排查，再根据实际口感微调。"
        )

    async def parse_dish_ingredients(self, dish_name: str) -> Dict[str, Any]:
        prompt = (
            f"请分析菜名“{dish_name}”，返回 JSON，字段包括：name、description、ingredients。"
            "ingredients 只返回食材名称数组，不要带克数。"
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一名专业中文菜谱顾问。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.6,
            "max_tokens": 800,
            "stream": False,
        }
        try:
            response_data = await self._post_json("/chat/completions", payload, timeout=30.0)
            return self._extract_json_object(self._extract_content(response_data))
        except Exception as exc:
            logger.warning("Parse dish ingredients failed, using fallback: %s", exc)
            return {
                "name": dish_name,
                "description": f"一道美味的{dish_name}",
                "ingredients": ["请根据实际情况补充食材"],
            }

    async def get_ingredient_recommendation(self, ingredients: List[str]) -> Dict[str, Any]:
        prompt = (
            f"我现在有这些食材：{', '.join(ingredients)}。"
            "请返回 JSON，字段包括 suggestedIngredients、recommendedDishes、nutritionTips。"
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一名专业食材搭配与营养建议助手。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": False,
        }
        try:
            response_data = await self._post_json("/chat/completions", payload, timeout=30.0)
            return self._extract_json_object(self._extract_content(response_data))
        except Exception as exc:
            logger.warning("Ingredient recommendation failed, using fallback: %s", exc)
            return {
                "suggestedIngredients": ["盐", "油", "酱油", "葱", "姜"],
                "recommendedDishes": ["家常小炒", "清炒时蔬", "简单快手菜"],
                "nutritionTips": "建议搭配蔬菜和优质蛋白，让营养更均衡。",
            }
