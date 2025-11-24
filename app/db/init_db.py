"""
数据库初始化脚本
用于创建数据库表结构
"""
from app.config.database import engine, Base
from app.models.user import User, RefreshTokenBlacklist

def init_db():
    """初始化数据库表"""
    print("开始创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")
    print("- users 表")
    print("- refresh_token_blacklist 表")

if __name__ == "__main__":
    init_db()

