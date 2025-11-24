"""
测试用户注册接口
"""
import requests
import json

BASE_URL = "http://localhost:8000"
REGISTER_URL = f"{BASE_URL}/api/auth/register"

def test_register():
    """测试用户注册"""
    print("=" * 50)
    print("测试用户注册接口")
    print("=" * 50)
    
    # 测试数据
    test_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    print(f"\n请求URL: {REGISTER_URL}")
    print(f"请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(REGISTER_URL, json=test_data)
        print(f"\n响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 检查响应体中的 code 字段（而不是 HTTP 状态码）
        response_code = result.get("code")
        if response_code == 201:
            print("\n✅ 注册成功！")
            user_data = result.get("data")
            if user_data:
                print(f"   用户ID: {user_data.get('id')}")
                print(f"   邮箱: {user_data.get('email')}")
                print(f"   状态: {user_data.get('state')}")
        else:
            print(f"\n❌ 注册失败 (code: {response_code})")
            print(f"   错误消息: {result.get('message')}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败，请确保服务器正在运行 (uvicorn main:app --reload)")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    test_register()

