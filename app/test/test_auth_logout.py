"""
测试用户退出登录接口
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000"
LOGOUT_URL = f"{BASE_URL}/api/auth/logout"

def load_tokens():
    """加载保存的token"""
    token_file = "app/test/tokens.json"
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return json.load(f)
    return None

def test_logout():
    """测试用户退出登录"""
    print("=" * 50)
    print("测试用户退出登录接口")
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
    
    print(f"\n请求URL: {LOGOUT_URL}")
    print(f"请求数据: refresh_token: {refresh_token[:50]}...")
    
    try:
        response = requests.post(LOGOUT_URL, json=test_data)
        print(f"\n响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        response_code = result.get("code")
        if response_code == 200:
            print("\n✅ 退出登录成功！")
            print("   Refresh token已加入黑名单")
            # 删除保存的token
            if os.path.exists("app/test/tokens.json"):
                os.remove("app/test/tokens.json")
                print("   已删除本地保存的token")
        elif response_code == 400:
            print("\n⚠️ 该token已失效")
        else:
            print(f"\n❌ 退出登录失败 (code: {response_code})")
            print(f"   错误消息: {result.get('message')}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败，请确保服务器正在运行 (uvicorn main:app --reload)")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    test_logout()

