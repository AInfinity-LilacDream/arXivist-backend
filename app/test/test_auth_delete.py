"""
测试删除用户接口
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000"
DELETE_URL = f"{BASE_URL}/api/auth/me"

def load_tokens():
    """加载保存的token"""
    token_file = "app/test/tokens.json"
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return json.load(f)
    return None

def test_delete_user():
    """测试删除当前用户"""
    print("=" * 50)
    print("测试删除用户接口")
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
    
    print(f"\n请求URL: {DELETE_URL}")
    print(f"请求方法: DELETE")
    print(f"请求头: Authorization: Bearer {access_token[:50]}...")
    print("\n⚠️  警告: 此操作将永久删除用户账号！")
    
    try:
        response = requests.delete(DELETE_URL, headers=headers)
        print(f"\n响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        response_code = result.get("code")
        if response_code == 200:
            print("\n✅ 用户账号删除成功！")
            # 删除保存的token
            if os.path.exists("app/test/tokens.json"):
                os.remove("app/test/tokens.json")
                print("   已删除本地保存的token")
        elif response_code == 401:
            print("\n❌ 认证失败，token可能已过期，请重新登录")
        else:
            print(f"\n❌ 删除用户失败 (code: {response_code})")
            print(f"   错误消息: {result.get('message')}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败，请确保服务器正在运行 (uvicorn main:app --reload)")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    test_delete_user()

