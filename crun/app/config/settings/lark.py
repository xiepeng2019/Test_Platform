from pydantic_settings import BaseSettings


class LarkSettings(BaseSettings):
    """Lark配置类"""
    LARK_CLIENT_ID: str
    LARK_SECRET: str
    LARK_REDIRECT_URI: str
