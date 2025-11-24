"""
测试获取论文列表接口
"""
import requests
import json

BASE_URL = "http://localhost:8000"
PAPERS_URL = f"{BASE_URL}/api/papers/"

def test_get_papers(start_date=None, max_results=10, category=None):
    """测试获取论文列表"""
    print("=" * 50)
    print("测试获取论文列表接口")
    print("=" * 50)
    
    params = {}
    if start_date:
        params["start_date"] = start_date
    if max_results:
        params["max_results"] = max_results
    if category:
        params["category"] = category
    
    print(f"\n请求URL: {PAPERS_URL}")
    if params:
        print(f"查询参数: {json.dumps(params, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.get(PAPERS_URL, params=params)
        print(f"\n响应状态码: {response.status_code}")
        
        result = response.json()
        print(f"响应消息: {result.get('message')}")
        
        if response.status_code == 200:
            print("\n✅ 获取论文列表成功！")
            data = result.get("data")
            if data:
                papers = data.get("papers", [])
                total = data.get("total", 0)
                date_range = data.get("date_range", "")
                print(f"   论文总数: {total}")
                print(f"   日期范围: {date_range}")
                print(f"\n   前3篇论文:")
                for i, paper in enumerate(papers[:3], 1):
                    print(f"\n   论文 {i}:")
                    print(f"     arXiv ID: {paper.get('arxiv_id')}")
                    print(f"     标题: {paper.get('title')[:80]}...")
                    print(f"     作者: {', '.join(paper.get('authors', [])[:3])}")
        else:
            print(f"\n❌ 获取论文列表失败")
            print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败，请确保服务器正在运行 (uvicorn main:app --reload)")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    # 测试默认查询（今日论文）
    print("\n【测试1】获取今日论文（默认）")
    test_get_papers(max_results=5)
    
    # 测试指定日期范围
    print("\n\n【测试2】获取指定日期范围的论文")
    test_get_papers(start_date="2025-01-01", max_results=5)
    
    # 测试指定类别
    print("\n\n【测试3】获取指定类别的论文")
    test_get_papers(category="cs.AI", max_results=5)

