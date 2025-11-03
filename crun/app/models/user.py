
from typing import Any

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, JSON, DateTime
from sqlalchemy.sql import func

from app.core.orm import Base



class User(SQLAlchemyBaseUserTable[int], Base):
    """用户模型"""
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, doc="用户ID")
    name: Mapped[str] = mapped_column(String(50), nullable=False, doc="用户名")
    en_name: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="英文名")
    union_id: Mapped[str | None] = mapped_column(String(100), nullable=True, doc="用户在飞书的唯一标识")
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True, doc="用户头像")
    permissions: Mapped[dict[str, list[str]] | None] = mapped_column(JSON, doc="用户权限", nullable=True, default={})
    extra: Mapped[dict[str, Any] | None] = mapped_column(JSON, doc="用户额外信息", nullable=True, default={})
    create_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now(), doc="用户创建时间")
    update_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), doc="用户更新时间")

    project_users = relationship(
        "ProjectUser",
        primaryjoin="User.id == foreign(ProjectUser.user_id)",
        lazy="selectin"
    )

    projects = relationship(
        "Project",
        secondary="project_user",
        primaryjoin="User.id == foreign(ProjectUser.user_id)",
        secondaryjoin="Project.id == foreign(ProjectUser.project_id)",
        viewonly=True  # 只读，避免多头管理中间表
    )