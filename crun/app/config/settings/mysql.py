from pydantic_settings import BaseSettings


class MysqlSettings(BaseSettings):
    """MySQL配置类"""
    MYSQL_ROOT_PASSWORD: str
    MYSQL_DATABASE: str
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASSWORD: str
