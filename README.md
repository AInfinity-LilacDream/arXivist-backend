# arXivist-backend

arXivist uses advanced AI (powered by GLM) to scan thousands of daily arXiv submissions and surface only the most insightful, rigorous, and impactful papers. No noise, no fluff—just high-signal research, thoughtfully scored and curated for curious minds.

## 项目结构

```
arXivist-backend/
├── app/                    # 主应用目录
│   ├── config/            # 配置文件
│   ├── db/                # 数据库相关脚本
│   ├── models/            # 数据模型
│   ├── routes/            # 路由定义
│   ├── services/          # 业务逻辑服务
│   └── test/              # 测试脚本
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

## 数据库初始化

首次运行前需要初始化数据库表结构：

```bash
python -m app.db.init_db
```

## 测试

项目提供了完整的API测试脚本，位于 `app/test/` 目录下。

### 运行所有测试

运行所有API接口的测试脚本：

```bash
python app/test/test_all.py
```

这会按顺序执行以下测试：
1. 用户注册
2. 用户登录
3. 获取用户信息
4. 刷新token
5. 获取论文列表
6. 获取论文详情
7. 退出登录
8. 删除用户

### 运行单个测试

你也可以单独运行某个测试脚本：

```bash
# 测试用户注册
python app/test/test_auth_register.py

# 测试用户登录
python app/test/test_auth_login.py

# 测试获取用户信息
python app/test/test_auth_me.py

# 测试刷新token
python app/test/test_auth_refresh.py

# 测试退出登录
python app/test/test_auth_logout.py

# 测试删除用户
python app/test/test_auth_delete.py

# 测试获取论文列表
python app/test/test_papers_list.py

# 测试获取论文详情
python app/test/test_papers_detail.py
```

### 测试前准备

1. **确保服务器正在运行**：
   ```bash
   uvicorn main:app --reload
   ```

2. **确保已安装所有依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **对于需要认证的接口**，测试脚本会自动从 `app/test/tokens.json` 读取token（登录测试会自动生成并保存token）。

### 注意事项

- 测试脚本使用默认邮箱 `test@example.com`，如需修改请编辑对应测试脚本
- Token会保存在 `app/test/tokens.json` 文件中（已添加到 `.gitignore`）
- 删除用户测试会永久删除测试账号，请谨慎使用