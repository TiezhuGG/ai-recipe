"""
测试食材推荐API
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.ai_service import AIService


async def test_recommendation():
    """测试食材推荐功能"""
    ai_service = AIService()
    
    print("测试1: 获取食材推荐")
    print("-" * 50)
    
    try:
        ingredients = ["番茄", "鸡蛋"]
        print(f"输入食材: {ingredients}")
        
        recommendation = await ai_service.get_ingredient_recommendation(ingredients)
        
        print("\n推荐结果:")
        print(f"建议添加的食材: {recommendation.get('suggestedIngredients', [])}")
        print(f"推荐菜谱: {recommendation.get('recommendedDishes', [])}")
        print(f"营养建议: {recommendation.get('nutritionTips', '')}")
        
        print("\n✅ 测试成功!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await ai_service.close()


async def test_parse_dish():
    """测试解析菜谱功能"""
    ai_service = AIService()
    
    print("\n\n测试2: 解析菜谱食材")
    print("-" * 50)
    
    try:
        dish_name = "红烧排骨"
        print(f"菜谱名称: {dish_name}")
        
        dish_info = await ai_service.parse_dish_ingredients(dish_name)
        
        print("\n解析结果:")
        print(f"名称: {dish_info.get('name', '')}")
        print(f"描述: {dish_info.get('description', '')}")
        print(f"所需食材: {dish_info.get('ingredients', [])}")
        
        print("\n✅ 测试成功!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await ai_service.close()


if __name__ == "__main__":
    print("=" * 50)
    print("食材推荐和菜谱解析功能测试")
    print("=" * 50)
    
    asyncio.run(test_recommendation())
    asyncio.run(test_parse_dish())
    
    print("\n" + "=" * 50)
    print("所有测试完成")
    print("=" * 50)
