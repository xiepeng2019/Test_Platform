import asyncio
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config.config import get_settings
from app.models import *


settings = get_settings()

""" 数据库配置 """
DATABASE_URL = f"mysql+asyncmy://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"

engine = create_async_engine(
    DATABASE_URL,  # postgresql+asyncpg://{username}:{password}@{host}:{port}/{db_name}
    echo=False,  # 是否打印出实际执行的 sql, 调试的时候可能更方便
    future=True,  # 使用 SQLAlchemy 2.0 API, 向后兼容
    max_overflow=10,  # 当连接池里的连接数已达到 pool_size 且都被使用时,
    pool_size=5,  # 接池中保持的连接数, 设置为 0 时表示连接无限制
    pool_recycle=60 * 20,  # 20 minutes, 设置时间以限制数据库自动断开
    pool_timeout=30.0,  # 如果超过这个时间, 还没有获得将会抛出异常
)
# async_sessionmaker：用于创建异步数据库会话的工具，避免重复配置会话参数，确保每次获取的会话都是独立的
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,  # 绑定到异步数据库引擎
    expire_on_commit=False,  # 提交后不过期会话，避免在异步环境中使用时出现问题
)

async def create_db_and_tables():
    """创建异步数据库和表"""
    for i in range(10):
        try:
            async with engine.begin() as conn: # 异步连接数据库
                await conn.run_sync(Base.metadata.create_all) # 创建所有表
            print("Database connection successful.")
            break
        except OperationalError as e: # 数据库连接失败时重试
            print(f"Database connection failed: {e}. Retrying in 5 seconds... ({i+1}/10)")
            await asyncio.sleep(5)
    else:
        print("Could not connect to the database after 10 retries.")
        raise
