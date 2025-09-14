from typing import Any

from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.orm import Base


class TestTaskRecord(Base):
    __tablename__ = "test_task_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, doc="测试任务记录的唯一标识")
    project_id: Mapped[int] = mapped_column(Integer, index=True, doc="该任务所属的项目ID")
    task_id: Mapped[int] = mapped_column(Integer, index=True, doc="该任务所属的测试任务ID")
    testplan_id: Mapped[int | None] = mapped_column(Integer, index=True, doc="关联的测试计划ID", nullable=True)
    agent_id: Mapped[int | None] = mapped_column(Integer, index=True, doc="关联的测试代理ID", nullable=True)
    creater: Mapped[str] = mapped_column(String(100), doc="创建此任务的用户")
    failed_continue: Mapped[int | None] = mapped_column(Integer, doc="如果一个测试失败，是否继续运行后续测试", nullable=True)
    status: Mapped[str | None] = mapped_column(String(100), doc="测试任务的当前状态", nullable=True)
    container_id: Mapped[str | None] = mapped_column(String(100), doc="测试任务的容器ID", nullable=True)
    logs: Mapped[str | None] = mapped_column(String(500), doc="测试任务的日志", nullable=True)
    branch: Mapped[str | None] = mapped_column(String(100), doc="测试任务的分支", nullable=True)
    image: Mapped[str | None] = mapped_column(String(100), doc="测试任务的镜像", nullable=True)
    repo: Mapped[str | None] = mapped_column(String(100), doc="测试任务的仓库", nullable=True)
    env_vars: Mapped[list[Any] | None] = mapped_column(JSON, doc="环境变量配置", nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), doc="任务创建时间")
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), doc="任务最后更新时间"
    )

    task = relationship(
        "TestTask",
        primaryjoin="foreign(TestTaskRecord.task_id) == TestTask.id",
        back_populates="records",
        lazy="selectin",
        viewonly=False,
    )

    case_records = relationship(
        "TestCaseRecord",
        primaryjoin="TestTaskRecord.id == foreign(TestCaseRecord.task_record_id)",
        lazy="selectin",
        viewonly=True,
        cascade="all, delete-orphan"
    )
