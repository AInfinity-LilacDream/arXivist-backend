"""
测试获取当前用户信息接口
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000"
ME_URL = f"{BASE_URL}/api/auth/me"

def load_tokens():
    """加载保存的token"""
    token_file = "app/test/tokens.json"
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return json.load(f)
    return None

def test_get_current_user():
    """测试获取当前用户信息"""
    print("=" * 50)
    print("测试获取当前用户信息接口")
    print("=" * 50)
    
    # 加载token
    tokens = load_tokens()
    if not tokens:
        print("\n❌ 未找到token，请先运行登录测试 (python app/test/test_auth_login.py)")
        return
    
    access_token = tokens.get("access_token")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    print(f"\n请求URL: {ME_URL}")
    print(f"请求头: Authorization: Bearer {access_token[:50]}...")
    
    try:
        response = requests.get(ME_URL, headers=headers)
        print(f"\n响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        response_code = result.get("code")
        if response_code == 200:
            print("\n✅ 获取用户信息成功！")
            user_data = result.get("data")
            if user_data:
                print(f"   用户ID: {user_data.get('id')}")
                print(f"   邮箱: {user_data.get('email')}")
                print(f"   状态: {user_data.get('state')}")
                print(f"   创建时间: {user_data.get('created_at')}")
        elif response_code == 401:
            print("\n❌ 认证失败，token可能已过期，请重新登录")
        else:
            print(f"\n❌ 获取用户信息失败 (code: {response_code})")
            print(f"   错误消息: {result.get('message')}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败，请确保服务器正在运行 (uvicorn main:app --reload)")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    test_get_current_user()

