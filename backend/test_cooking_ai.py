"""
测试烹饪AI功能
"""
import asyncio
import sys
from app.services.ai_service import AIService
from app.core.config import settings


async def test_cooking_question():
    """测试烹饪问题回答"""
    print("=" * 60)
    print("测试烹饪问题回答功能")
    print("=" * 60)
    
    # 检查配置
    print(f"\n配置信息:")
    print(f"API Key (前8位): {settings.LLM_API_KEY[:8]}...")
    print(f"API Base URL: {settings.LLM_API_BASE_URL}")
    print(f"Model Name: {settings.MODEL_NAME}")
    
    ai_service = AIService()
    
    test_questions = [
        "如何让肉更嫩？",
        "炒菜怎么不粘锅？",
        "如何掌握火候？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'=' * 60}")
        print(f"测试问题 {i}: {question}")
        print(f"{'=' * 60}")
        
        try:
            answer = await ai_service.answer_cooking_question(question)
            print(f"\n回答:")
            print(answer)
            print(f"\n✅ 测试成功")
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
    
    await ai_service.close()


async def test_cooking_diagnosis():
    """测试烹饪问题诊断"""
    print("\n" + "=" * 60)
    print("测试烹饪问题诊断功能")
    print("=" * 60)
    
    ai_service = AIService()
    
    test_problems = [
        "炒出来的菜太咸了",
        "肉炒不熟",
        "青菜炒出来发黄"
    ]
    
    for i, problem in enumerate(test_problems, 1):
        print(f"\n{'=' * 60}")
        print(f"测试问题 {i}: {problem}")
        print(f"{'=' * 60}")
        
        try:
            diagnosis = await ai_service.diagnose_cooking_problem(problem)
            print(f"\n诊断结果:")
            print(diagnosis)
            print(f"\n✅ 测试成功")
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
    
    await ai_service.close()


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("开始测试烹饪AI功能")
    print("=" * 60)
    
    # 测试问题回答
    await test_cooking_question()
    
    # 测试问题诊断
    await test_cooking_diagnosis()
    
    print("\n" + "=" * 60)
    print("所有测试完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")
        sys.exit(1)
