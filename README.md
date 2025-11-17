# arXivist-backend

arXivist uses advanced AI (powered by GLM) to scan thousands of daily arXiv submissions and surface only the most insightful, rigorous, and impactful papers. No noise, no fluff—just high-signal research, thoughtfully scored and curated for curious minds.

## 项目结构

```
arXivist-backend/
├── app/                    # 主应用目录
│   ├── config/            # 配置文件
│   ├── models/            # 数据模型
│   ├── routes/            # 路由定义
│   └── services/          # 业务逻辑服务
├── docs/                  # 文档目录
├── main.py                # 应用入口
└── requirements.txt       # 项目依赖

## 技术栈

- **框架**: FastAPI
- **Python**: 3.8+
- **主要依赖**: arxiv, pydantic, uvicorn

## 快速开始

### 1. 环境要求

- Python 3.8 或更高版本
- pip（Python 包管理器）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

```bash
uvicorn main:app --reload
```

### 4. 访问服务

启动成功后，服务默认运行在 `http://localhost:8000`

- **API 文档 (Swagger UI)**: http://localhost:8000/docs
- **API 文档 (ReDoc)**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## API 使用示例

### 获取今日论文（默认）

```bash
GET http://localhost:8000/api/papers/
```

### 获取从指定日期到今天的论文

```bash
GET http://localhost:8000/api/papers/?start_date=2025-01-01&max_results=50
```

### 获取特定类别的论文

```bash
GET http://localhost:8000/api/papers/?category=cs.AI&max_results=20
```

### 使用 curl 示例

```bash
# 获取今日论文
curl "http://localhost:8000/api/papers/"

# 获取从指定日期到今天的论文
curl "http://localhost:8000/api/papers/?start_date=2025-01-01&max_results=50"

# 获取特定类别的论文
curl "http://localhost:8000/api/papers/?category=cs.AI&max_results=20"
```

## API 参数说明

| 参数          | 类型   | 必填 | 默认值 | 说明                                                 |
| ------------- | ------ | ---- | ------ | ---------------------------------------------------- |
| `start_date`  | date   | 否   | 当日   | 开始日期，格式：YYYY-MM-DD。查询从该日期到当天的论文 |
| `max_results` | int    | 否   | 100    | 最大返回数量，范围：1-2000                           |
| `category`    | string | 否   | -      | 论文类别，如 cs.AI, cs.CV 等                         |