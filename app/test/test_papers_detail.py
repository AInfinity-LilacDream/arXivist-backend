"""
测试获取论文详情接口
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_get_paper_detail(arxiv_id: str):
    """测试获取论文详情"""
    print("=" * 50)
    print("测试获取论文详情接口")
    print("=" * 50)
    
    url = f"{BASE_URL}/api/papers/{arxiv_id}"
    
    print(f"\n请求URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"\n响应状态码: {response.status_code}")
        
        result = response.json()
        print(f"响应消息: {result.get('message')}")
        
        if response.status_code == 200:
            print("\n✅ 获取论文详情成功！")
            paper = result.get("data")
            if paper:
                print(f"\n   论文信息:")
                print(f"     arXiv ID: {paper.get('arxiv_id')}")
                print(f"     标题: {paper.get('title')}")
                print(f"     作者: {', '.join(paper.get('authors', []))}")
                print(f"     摘要: {paper.get('summary')[:200]}...")
                print(f"     提交日期: {paper.get('published')}")
                print(f"     PDF链接: {paper.get('pdf_url')}")
                print(f"     分类: {', '.join(paper.get('categories', []))}")
        elif response.status_code == 404:
            print(f"\n❌ 未找到 arXiv ID 为 {arxiv_id} 的论文")
        else:
            print(f"\n❌ 获取论文详情失败")
            print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败，请确保服务器正在运行 (uvicorn main:app --reload)")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    # 测试获取论文详情
    test_get_paper_detail("2511.11570")
    
    # 测试不存在的论文ID
    print("\n\n【测试2】测试不存在的论文ID")
    test_get_paper_detail("9999.99999")

