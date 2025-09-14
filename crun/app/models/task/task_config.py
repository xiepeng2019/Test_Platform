from typing import Any

from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.orm import Base
from app.models import User


class TaskConfig(Base):
    """Represents a task configuration for test execution."""
    __tablename__ = "task_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, doc="任务配置的唯一标识")
    name: Mapped[str] = mapped_column(String(100), doc="任务配置的名称")
    project_id: Mapped[int] = mapped_column(Integer, index=True, doc="该配置所属的项目ID")
    owner_id: Mapped[int] = mapped_column(Integer, index=True, doc="拥有或负责此配置的用户")
    description: Mapped[str | None] = mapped_column(String(500), doc="任务配置的描述", nullable=True)
    env_vars: Mapped[list[Any] | None] = mapped_column(JSON, doc="环境变量配置", nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), doc="配置创建时间")
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), doc="配置最后更新时间"
    )

    owner: Mapped["User"] = relationship(
        "User",
        primaryjoin="foreign(TaskConfig.owner_id) == User.id",
        lazy="joined",
    )