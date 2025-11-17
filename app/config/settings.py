from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    app_name: str = "arXivist Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API 配置
    api_prefix: str = "/api"
    
    # arXiv API 配置
    arxiv_max_results: int = 2000
    arxiv_default_results: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

