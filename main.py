from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import paper_routes
from app.config.settings import settings

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="arXivist Backend - 每日 arXiv 论文检索服务"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应设置为具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(paper_routes.router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用 arXivist Backend API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

