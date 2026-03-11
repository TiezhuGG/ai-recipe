"""
测试当前API配置
"""
import asyncio
import httpx
from app.core.config import settings


async def test_api():
    """测试当前API配置"""
    print("=" * 60)
    print("测试当前API配置")
    print("=" * 60)
    
    print(f"\n配置信息:")
    print(f"API Key (前8位): {settings.LLM_API_KEY[:8]}...")
    print(f"API Base URL: {settings.LLM_API_BASE_URL}")
    print(f"Model Name: {settings.MODEL_NAME}")
    
    # 构建测试请求
    request_body = {
        "model": settings.MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一位经验丰富的烹饪导师。"},
            {"role": "user", "content": "如何让肉更嫩？"}
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
        "stream": False
    }
    
    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"\n发送测试请求...")
    print(f"URL: {settings.LLM_API_BASE_URL}/chat/completions")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{settings.LLM_API_BASE_URL}/chat/completions",
                json=request_body,
                headers=headers
            )
            
            print(f"\n响应状态码: {response.status_code}")
            print(f"\n响应内容:")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"完整响应: {response_data}")
                
                # 尝试解析
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    answer = response_data["choices"][0]["message"]["content"]
                    print(f"\n✅ 成功解析回答:")
                    print(answer)
                else:
                    print(f"\n❌ 响应格式不正确，缺少choices字段")
            else:
                print(f"❌ API返回错误: {response.text}")
                
        except Exception as e:
            print(f"\n❌ 请求失败: {e.__class__.__name__} - {e}")


if __name__ == "__main__":
    asyncio.run(test_api())
