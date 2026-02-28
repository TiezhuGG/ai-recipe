"""
API端点测试脚本
用于验证后端功能是否正常工作
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health_check():
    """测试健康检查端点"""
    print("\n=== 测试健康检查 ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    assert response.status_code == 200
    print("✓ 健康检查通过")


def test_generate_recipe():
    """测试菜谱生成端点"""
    print("\n=== 测试菜谱生成 ===")
    
    data = {
        "ingredients": ["鸡胸肉", "西兰花", "胡萝卜"],
        "flavor_tags": ["健康", "低脂"],
        "cuisine_types": ["中餐"],
        "special_groups": ["健身人群"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/recipes/generate",
        json=data
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        recipe = response.json()
        print(f"菜谱名称: {recipe.get('name')}")
        print(f"难度: {recipe.get('difficulty')}")
        print(f"烹饪时间: {recipe.get('cooking_time')}分钟")
        print("✓ 菜谱生成成功")
        
        # 保存session_id用于后续测试
        session_id = response.cookies.get('session_id')
        return session_id, recipe
    else:
        print(f"错误: {response.text}")
        return None, None


def test_save_recipe(session_id, recipe):
    """测试菜谱保存端点"""
    print("\n=== 测试菜谱保存 ===")
    
    if not session_id or not recipe:
        print("⚠ 跳过测试（需要先生成菜谱）")
        return None
    
    cookies = {"session_id": session_id}
    response = requests.post(
        f"{BASE_URL}/api/recipes/save",
        json=recipe,
        cookies=cookies
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"菜谱ID: {result.get('id')}")
        print(f"保存状态: {result.get('success')}")
        print("✓ 菜谱保存成功")
        return result.get('id')
    else:
        print(f"错误: {response.text}")
        return None


def test_get_history(session_id):
    """测试历史记录端点"""
    print("\n=== 测试历史记录 ===")
    
    if not session_id:
        print("⚠ 跳过测试（需要session_id）")
        return
    
    cookies = {"session_id": session_id}
    response = requests.get(
        f"{BASE_URL}/api/recipes/history",
        cookies=cookies
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"菜谱数量: {result.get('total')}")
        print("✓ 历史记录查询成功")
    else:
        print(f"错误: {response.text}")


def test_get_recipe_detail(session_id, recipe_id):
    """测试菜谱详情端点"""
    print("\n=== 测试菜谱详情 ===")
    
    if not session_id or not recipe_id:
        print("⚠ 跳过测试（需要session_id和recipe_id）")
        return
    
    cookies = {"session_id": session_id}
    response = requests.get(
        f"{BASE_URL}/api/recipes/{recipe_id}",
        cookies=cookies
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        recipe = response.json()
        print(f"菜谱名称: {recipe.get('name')}")
        print("✓ 菜谱详情查询成功")
    else:
        print(f"错误: {response.text}")


def main():
    """运行所有测试"""
    print("=" * 50)
    print("开始测试后端API")
    print("=" * 50)
    
    try:
        # 1. 健康检查
        test_health_check()
        
        # 2. 生成菜谱
        session_id, recipe = test_generate_recipe()
        
        # 3. 保存菜谱
        recipe_id = test_save_recipe(session_id, recipe)
        
        # 4. 查询历史
        test_get_history(session_id)
        
        # 5. 查询详情
        test_get_recipe_detail(session_id, recipe_id)
        
        print("\n" + "=" * 50)
        print("所有测试完成！")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到服务器")
        print("请确保后端服务正在运行: python backend/main.py")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")


if __name__ == "__main__":
    main()
