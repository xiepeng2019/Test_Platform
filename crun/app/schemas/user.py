from typing import List, Any, Dict
import uuid

from fastapi_users import schemas
from pydantic import ConfigDict, field_validator, BaseModel

from app.config.config import get_settings


settings = get_settings()


class UserRead(schemas.BaseUser[uuid.UUID]):
    """用户读取模型"""
    id: int
    name: str
    en_name: str | None = None
    extra: Dict[str, Any] | None = {}
    union_id: str | None = None
    avatar: str | None = None
    permissions: Dict[str, List[str]] | None = {}

    @field_validator("avatar", mode="before")
    def transform_avatar_url(cls, v: str | None) -> str | None:
        """转换头像URL为完整URL"""
        if v and not v.startswith("http"):
            return f"{settings.STATIC_URL}{v}"
        return v


class UserCreate(schemas.BaseUserCreate):
    """用户创建模型"""
    name: str
    en_name: str | None = None
    avatar: str | None = None
    union_id: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    """用户更新模型"""
    name: str | None = None
    en_name: str | None = None


class UserInfo(schemas.BaseUser[uuid.UUID]):
    """用户信息模型"""
    id: int
    name: str
    en_name: str | None = None
    union_id: str | None = None


class UserSearch(BaseModel):
    """用户搜索模型"""
    id: int
    email: str
    name: str
    en_name: str | None = None
    union_id: str | None = None
    avatar: str | None = None

    @field_validator("avatar", mode="before")
    def transform_avatar_url(cls, v: str | None) -> str | None:
        """转换头像URL为完整URL"""
        if v and not v.startswith("http"):
            return f"{settings.STATIC_URL}{v}"
        return v

    model_config = ConfigDict(from_attributes=True)


class UpdateUserAvatar(BaseModel):
    """更新用户头像模型"""
    avatar: str