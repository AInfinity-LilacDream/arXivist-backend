"""
运行所有测试脚本
"""
import subprocess
import sys
import os

def run_test(script_name):
    """运行单个测试脚本"""
    print("\n" + "=" * 70)
    print(f"运行测试: {script_name}")
    print("=" * 70)
    script_path = os.path.join("app", "test", script_name)
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"运行测试失败: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("=" * 70)
    print("开始运行所有API测试")
    print("=" * 70)
    
    # 测试顺序
    tests = [
        "test_auth_register.py",      # 1. 注册
        "test_auth_login.py",         # 2. 登录
        "test_auth_me.py",            # 3. 获取用户信息
        "test_auth_refresh.py",       # 4. 刷新token
        "test_papers_list.py",        # 5. 获取论文列表
        "test_papers_detail.py",      # 6. 获取论文详情
        "test_auth_logout.py",        # 7. 退出登录
        "test_auth_delete.py",        # 8. 删除用户（注意：会删除账号，应在最后执行）
    ]
    
    results = {}
    for test in tests:
        success = run_test(test)
        results[test] = success
    
    # 打印总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    for test, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test}: {status}")

if __name__ == "__main__":
    main()

