"""
测试用户登录接口
"""
import requests
import json

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"

def test_login(email: str = "test@example.com", password: str = "password123"):
    """测试用户登录"""
    print("=" * 50)
    print("测试用户登录接口")
    print("=" * 50)
    
    # 测试数据
    test_data = {
        "email": email,
        "password": password
    }
    
    print(f"\n请求URL: {LOGIN_URL}")
    print(f"请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(LOGIN_URL, json=test_data)
        print(f"\n响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 检查响应体中的 code 字段
        response_code = result.get("code")
        if response_code == 200:
            print("\n✅ 登录成功！")
            token_data = result.get("data")
            if token_data:
                print(f"   Access Token: {token_data.get('access_token')[:50]}...")
                print(f"   Refresh Token: {token_data.get('refresh_token')[:50]}...")
                print(f"   Token Type: {token_data.get('token_type')}")
                # 保存token供其他测试使用
                with open("app/test/tokens.json", "w") as f:
                    json.dump(token_data, f, indent=2)
                print("\n   已保存token到 app/test/tokens.json")
            return token_data
        else:
            print(f"\n❌ 登录失败 (code: {response_code})")
            print(f"   错误消息: {result.get('message')}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败，请确保服务器正在运行 (uvicorn main:app --reload)")
        return None
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return None


if __name__ == "__main__":
    test_login()

