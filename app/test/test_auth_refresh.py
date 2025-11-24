"""
测试刷新token接口
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000"
REFRESH_URL = f"{BASE_URL}/api/auth/refresh"

def load_tokens():
    """加载保存的token"""
    token_file = "app/test/tokens.json"
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return json.load(f)
    return None

def test_refresh_token():
    """测试刷新token"""
    print("=" * 50)
    print("测试刷新token接口")
    print("=" * 50)
    
    # 加载token
    tokens = load_tokens()
    if not tokens:
        print("\n❌ 未找到token，请先运行登录测试 (python app/test/test_auth_login.py)")
        return
    
    refresh_token = tokens.get("refresh_token")
    test_data = {
        "refresh_token": refresh_token
    }
    
    print(f"\n请求URL: {REFRESH_URL}")
    print(f"请求数据: refresh_token: {refresh_token[:50]}...")
    
    try:
        response = requests.post(REFRESH_URL, json=test_data)
        print(f"\n响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        response_code = result.get("code")
        if response_code == 200:
            print("\n✅ 刷新token成功！")
            token_data = result.get("data")
            if token_data:
                print(f"   新 Access Token: {token_data.get('access_token')[:50]}...")
                print(f"   新 Refresh Token: {token_data.get('refresh_token')[:50]}...")
                # 更新保存的token
                with open("app/test/tokens.json", "w") as f:
                    json.dump(token_data, f, indent=2)
                print("\n   已更新token到 app/test/tokens.json")
        elif response_code == 401:
            print("\n❌ 刷新失败，refresh token可能已过期或已失效")
        else:
            print(f"\n❌ 刷新token失败 (code: {response_code})")
            print(f"   错误消息: {result.get('message')}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败，请确保服务器正在运行 (uvicorn main:app --reload)")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    test_refresh_token()

