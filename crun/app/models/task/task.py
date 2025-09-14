from typing import Any

from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy.sql import func

from app.core.orm import Base
from app.models.user import User
from app.models.resource.server import Server
from app.models.task.task_config import TaskConfig


class TestTaskCases(Base):
    __tablename__ = "test_task_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    task_id: Mapped[int] = mapped_column(Integer, index=True)
    case_index: Mapped[str] = mapped_column(String(100), index=True)

    # 逻辑外键关联 User，没有外键约束，使用 foreign() 明确外键引用
    cases = relationship(
        "TestCase",
        primaryjoin="TestTaskCases.case_index == foreign(TestCase.index)",
        lazy="selectin",
        uselist=False
    )

    task = relationship(
        "TestTask",
        primaryjoin="TestTaskCases.task_id == foreign(TestTask.id)",
        lazy="selectin",
    )


class TestTask(Base):
    """Represents a test task, which is an executable instance of a test plan."""
    __tablename__ = "test_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, doc="测试任务的唯一标识")
    name: Mapped[str] = mapped_column(String(100), doc="测试任务的名称")
    project_id: Mapped[int] = mapped_column(Integer, index=True, doc="该任务所属的项目ID")
    testplan_id: Mapped[int | None] = mapped_column(Integer, index=True, doc="关联的测试计划ID", nullable=True)
    owner_id: Mapped[str] = mapped_column(String(100), index=True, doc="拥有或负责此任务的用户")
    config_id: Mapped[int | None] = mapped_column(Integer, index=True, doc="测试任务的配置ID", nullable=True)
    failed_continue: Mapped[int | None] = mapped_column(Integer, doc="如果一个测试失败，是否继续运行后续测试", nullable=True)
    server_id: Mapped[int | None] = mapped_column(Integer, doc="测试环境ID", nullable=True)
    status: Mapped[str | None] = mapped_column(String(100), doc="测试任务的当前状态", nullable=True)
    lark_notice: Mapped[int | None] = mapped_column(Integer, doc="飞书通知的配置", nullable=True)
    lark_subscribe: Mapped[list[Any] | None] = mapped_column(JSON, doc="用于通知的飞书用户Open ID列表", nullable=True)
    desc: Mapped[str | None] = mapped_column(String(500), doc="测试任务的描述", nullable=True)
    comment: Mapped[str | None] = mapped_column(String(500), doc="关于任务的可选注释或说明", nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), doc="任务创建时间")
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), doc="任务最后更新时间"
    )

    config: Mapped[TaskConfig] = relationship(
        "TaskConfig",
        primaryjoin="foreign(TestTask.config_id) == TaskConfig.id",
        lazy="joined",
    )

    server: Mapped[Server] = relationship(
        "Server",
        primaryjoin="foreign(TestTask.server_id) == Server.id",
        lazy="joined",
    )

    owner: Mapped[User] = relationship(
        "User",
        primaryjoin="foreign(TestTask.owner_id) == User.id",
        lazy="joined",
    )

    cases = relationship(
        "TestCase",
        secondary="test_task_cases",
        primaryjoin="TestTask.id == foreign(TestTaskCases.task_id)",
        secondaryjoin="TestCase.index == foreign(TestTaskCases.case_index)",
        lazy="selectin"
    )

    records = relationship(
        "TestTaskRecord",
        primaryjoin="TestTask.id == foreign(TestTaskRecord.task_id)",
        back_populates="task",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
