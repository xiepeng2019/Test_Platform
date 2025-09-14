from multiprocessing import cpu_count
from functools import cache

from pydantic_settings import SettingsConfigDict

from .settings.dir import get_work_dir
from .settings.mysql import Settings as MysqlSettings
from .settings.lark import LarkSettings


_WORK_DIR = get_work_dir()


class Settings(LarkSettings, MysqlSettings):
    SECRET_KEY: str
    NAME: str
    FRONTEND_URL: str
    STATIC_URL: str
    JWT_EXPIRATION_TIME: int

    ENV: str = "development"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    WORKERS: int = cpu_count()
    URL: str = "http://localhost"
    TIME_ZONE: str = "RPC"
    # HOST_GATEWAY: str = "host.docker.internal"
    HOST_GATEWAY: str = "172.17.0.1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@cache
def get_settings() -> Settings:
    """lru_cache 保证了只有在第一次调用它时才会创建 Settings 对象一次
        https://fastapi.tiangolo.com/zh/advanced/settings/#__tabbed_4_1

        .env 中 ENV 决定了开发环境

    Returns:
        _type_: _description_
    """

    return Settings()  # pyright: ignore[reportCallIssue]
