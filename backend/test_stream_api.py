"""
测试流式API
"""
import asyncio
from app.services.ai_service import AIService


async def test_stream():
    """测试流式输出"""
    print("=" * 60)
    print("测试流式AI对话")
    print("=" * 60)
    
    ai_service = AIService()
    
    question = "如何让肉更嫩？请详细说明至少5种方法。"
    print(f"\n问题: {question}\n")
    print("AI回答（流式）:")
    print("-" * 60)
    
    try:
        full_answer = ""
        chunk_count = 0
        
        async for chunk in ai_service.answer_cooking_question_stream(question):
            print(chunk, end='', flush=True)
            full_answer += chunk
            chunk_count += 1
        
        print("\n" + "-" * 60)
        print(f"\n✅ 流式输出成功")
        print(f"完整回答长度: {len(full_answer)} 字符")
        print(f"接收到的块数: {chunk_count}")
        print(f"\n完整回答:\n{full_answer}")
        
    except Exception as e:
        print(f"\n❌ 流式输出失败: {e}")
        import traceback
        traceback.print_exc()
    
    await ai_service.close()


if __name__ == "__main__":
    asyncio.run(test_stream())
