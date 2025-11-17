# arXiv API 调研报告

## 概述

arXiv 提供了官方的 RESTful API，允许开发者以编程方式访问其论文数据库。通过该 API，可以检索特定时间段内的新论文，非常适合构建每日更新 arXiv 论文的网站。

## API 端点

**基础 URL：** `http://export.arxiv.org/api/query`

## API 特点

- **免费使用**：无需 API Key，可直接访问
- **RESTful 风格**：基于 HTTP GET 请求
- **返回格式**：XML（Atom 格式）
- **无速率限制**：但建议合理使用，避免过于频繁的请求

## 查询参数

### 主要参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `search_query` | 搜索查询条件 | `all`（所有论文）、`cat:cs.AI`（特定类别） |
| `start` | 结果起始位置（分页） | `0`、`10`、`20` |
| `max_results` | 返回结果的最大数量 | `10`、`25`、`100`（建议不超过 2000） |
| `sortBy` | 排序字段 | `submittedDate`（提交日期）、`relevance`（相关性）、`lastUpdatedDate`（最后更新日期） |
| `sortOrder` | 排序顺序 | `ascending`（升序）、`descending`（降序） |

### 搜索查询语法

`search_query` 支持多种查询语法：

- **所有论文**：`all`
- **按类别**：`cat:cs.AI`（计算机科学-人工智能）
- **按标题**：`ti:neural`
- **按作者**：`au:smith`
- **按摘要**：`abs:machine learning`
- **组合查询**：`cat:cs.AI AND ti:transformer`
- **日期范围**：`submittedDate:[20250101*TO*20250117*]`（注意：日期格式为 YYYYMMDD）

### 日期范围查询示例

获取指定日期范围内的论文：

```
http://export.arxiv.org/api/query?search_query=submittedDate:[20250101*TO*20250117*]&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending
```

## 返回数据格式

API 返回 XML 格式（Atom Feed），包含以下信息：

- **标题** (`title`)
- **作者** (`author`)
- **摘要** (`summary`)
- **提交日期** (`published`)
- **最后更新日期** (`updated`)
- **论文 ID** (`id`)
- **PDF 链接** (`link`)
- **分类** (`category`)
- **DOI** (`arxiv:doi`)

## 使用示例

### 1. 使用 Python requests 库

```python
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

def get_recent_papers(days=1, max_results=10):
    """
    获取最近 N 天的论文
    
    Args:
        days: 天数，默认为 1 天
        max_results: 最大返回数量
    """
    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 格式化日期为 YYYYMMDD
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    
    # 构建查询 URL
    url = f'http://export.arxiv.org/api/query'
    params = {
        'search_query': f'submittedDate:[{start_str}*TO*{end_str}*]',
        'start': 0,
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    # 发送请求
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # 解析 XML
        root = ET.fromstring(response.content)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        
        papers = []
        for entry in root.findall('atom:entry', namespace):
            paper = {
                'title': entry.find('atom:title', namespace).text.strip(),
                'published': entry.find('atom:published', namespace).text,
                'summary': entry.find('atom:summary', namespace).text.strip(),
                'authors': [author.find('atom:name', namespace).text 
                           for author in entry.findall('atom:author', namespace)],
                'id': entry.find('atom:id', namespace).text,
                'categories': [cat.get('term') 
                             for cat in entry.findall('atom:category', namespace)]
            }
            papers.append(paper)
        
        return papers
    else:
        print(f"请求失败，状态码：{response.status_code}")
        return []

# 使用示例
papers = get_recent_papers(days=1, max_results=10)
for paper in papers:
    print(f"标题：{paper['title']}")
    print(f"提交日期：{paper['published']}")
    print(f"作者：{', '.join(paper['authors'])}")
    print("---")
```

### 2. 使用 arxiv Python 库（推荐）

`arxiv` 是一个第三方 Python 库，封装了 arXiv API，使用更加便捷。

**安装：**
```bash
pip install arxiv
```

**使用示例：**
```python
import arxiv
from datetime import datetime, timedelta

def get_recent_papers_with_library(days=1, max_results=10):
    """
    使用 arxiv 库获取最近 N 天的论文
    """
    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 格式化日期
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    
    # 构建查询
    query = f'submittedDate:[{start_str}*TO*{end_str}*]'
    
    # 执行搜索
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    
    papers = []
    for result in search.results():
        papers.append({
            'title': result.title,
            'authors': [author.name for author in result.authors],
            'summary': result.summary,
            'published': result.published,
            'updated': result.updated,
            'entry_id': result.entry_id,
            'pdf_url': result.pdf_url,
            'categories': result.categories
        })
    
    return papers

# 使用示例
papers = get_recent_papers_with_library(days=1, max_results=10)
for paper in papers:
    print(f"标题：{paper['title']}")
    print(f"作者：{', '.join(paper['authors'])}")
    print(f"摘要：{paper['summary'][:200]}...")
    print(f"PDF：{paper['pdf_url']}")
    print("---")
```

### 3. 获取最新论文（不指定日期范围）

如果只需要获取最新提交的论文，可以简化查询：

```python
import arxiv

# 获取最新 10 篇论文
search = arxiv.Search(
    query="all",
    max_results=10,
    sort_by=arxiv.SortCriterion.SubmittedDate,
    sort_order=arxiv.SortOrder.Descending
)

for result in search.results():
    print(f"标题：{result.title}")
    print(f"提交日期：{result.published}")
    print(f"链接：{result.entry_id}")
    print("\n")
```

## 论文类别

arXiv 论文按学科分类，常见类别包括：

- **计算机科学**：`cs.AI`（人工智能）、`cs.CV`（计算机视觉）、`cs.LG`（机器学习）、`cs.CL`（计算语言学）等
- **数学**：`math.OC`（优化与控制）、`math.ST`（统计理论）等
- **物理**：`physics`、`quant-ph`（量子物理）等
- **其他**：`eess`（电气工程与系统科学）、`q-bio`（定量生物学）等

完整类别列表：https://arxiv.org/help/api/user-manual#subject_classifications

## 最佳实践

1. **合理设置 max_results**：建议不超过 2000，避免单次请求过大
2. **使用分页**：通过 `start` 参数实现分页加载
3. **缓存结果**：避免重复请求相同的数据
4. **错误处理**：添加适当的错误处理和重试机制
5. **速率控制**：虽然无官方限制，但建议控制请求频率，避免对服务器造成压力

## 时间范围查询注意事项

1. **日期格式**：必须使用 `YYYYMMDD` 格式（如 `20250117`）
2. **日期范围语法**：`submittedDate:[YYYYMMDD*TO*YYYYMMDD*]`
3. **时区**：arXiv 使用 UTC 时区
4. **最新论文**：如果不指定日期范围，使用 `sortBy=submittedDate&sortOrder=descending` 获取最新论文

## 参考资料

- **arXiv API 用户手册**：https://arxiv.org/help/api/user-manual
- **arXiv API 文档**：https://arxiv.org/help/api
- **Python arxiv 库**：https://pypi.org/project/arxiv/
- **arXiv 类别列表**：https://arxiv.org/help/api/user-manual#subject_classifications

## 总结

arXiv 提供了完善的官方 API，支持：
- ✅ 按日期范围查询论文
- ✅ 按类别、作者、标题等条件筛选
- ✅ 排序和分页功能
- ✅ 免费使用，无需 API Key
- ✅ 返回完整的论文元数据

对于构建每日刷 arXiv 论文的网站，该 API 完全满足需求。建议使用 Python 的 `arxiv` 库来简化 API 调用，或者直接使用 HTTP 请求配合 XML 解析。

