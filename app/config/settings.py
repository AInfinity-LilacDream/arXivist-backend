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
    
    # 数据库配置
    db_user: str = "arxivist"
    db_password: str = "arxivist"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "arXivist"
    
    # JWT 配置
    jwt_secret_key: str = "arxivist123123"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15  # access token 15分钟
    refresh_token_expire_days: int = 7  # refresh token 7天
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        """构建数据库连接URL"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()

