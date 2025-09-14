from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models import User
from app.core.orm import Base
from sqlalchemy.orm import relationship


class TestPlanCases(Base):
    __tablename__ = "test_plan_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    plan_id: Mapped[int] = mapped_column(Integer, index=True)
    case_index: Mapped[str] = mapped_column(String(100), index=True)

    # 逻辑外键关联 User，没有外键约束，使用 foreign() 明确外键引用
    cases = relationship(
        "TestCase",
        primaryjoin="TestPlanCases.case_index == foreign(TestCase.index)",
        lazy="selectin",
        uselist=False
    )

    plan = relationship(
        "TestPlan",
        primaryjoin="TestPlanCases.plan_id == foreign(TestPlan.id)",
        lazy="selectin",
    )


class TestPlan(Base):
    """Represents a test plan, which is a collection of test cases."""
    __tablename__ = "test_plan"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, doc="测试计划的唯一标识")
    name: Mapped[str] = mapped_column(String(100), doc="测试计划的名称")
    project_id: Mapped[int] = mapped_column(Integer, index=True, doc="该计划所属的项目ID")
    stage: Mapped[int | None] = mapped_column(Integer, doc="测试计划的当前阶段", nullable=True)
    owner_id: Mapped[str] = mapped_column(String(100), index=True, doc="拥有或负责此计划的用户")
    status: Mapped[int | None] = mapped_column(Integer, doc="测试计划的当前状态", nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), doc="任务创建时间")
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), doc="任务最后更新时间"
    )

    owner: Mapped["User"] = relationship(
        "User",
        primaryjoin="foreign(TestPlan.owner_id) == User.id",
        lazy="joined",
    )
    cases = relationship(
        "TestCase",
        secondary="test_plan_cases",
        primaryjoin="TestPlan.id == foreign(TestPlanCases.plan_id)",
        secondaryjoin="TestCase.index == foreign(TestPlanCases.case_index)",
        lazy="selectin",
        viewonly=True,
    )
