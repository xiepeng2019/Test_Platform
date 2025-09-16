from typing import Any
from sqlalchemy import UniqueConstraint, Integer, String, DateTime, JSON, Boolean, Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func
from app.core.orm import Base


class TestCase(Base):
    """Represents a single test case within a project."""
    __tablename__ = "testcases"
    __table_args__ = (
        UniqueConstraint("project_id", "index", name="uq_project_index"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, doc="测试用例唯一标识")
    name: Mapped[str] = mapped_column(String(255), index=True, doc="测试用例名称")
    test_type: Mapped[str | None] = mapped_column(String(255), doc="测试用例类型 (例如, 功能测试, 性能测试)", nullable=True)
    index: Mapped[str | None] = mapped_column(String(255), index=True, doc="测试用例的唯一索引或标识符", nullable=True)
    expected: Mapped[str | None] = mapped_column(Text, doc="测试用例的预期结果", nullable=True)
    module: Mapped[str | None] = mapped_column(String(255), doc="该测试用例所属的模块或功能区", nullable=True)
    node_id: Mapped[int | None] = mapped_column(Integer, index=True, doc="关联的测试用例节点ID", nullable=True)
    objective: Mapped[str | None] = mapped_column(Text, doc="测试用例的目标", nullable=True)
    priority: Mapped[str | None] = mapped_column(String(255), doc="测试用例的优先级 (例如, P0, P1)", nullable=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True, doc="该测试用例所属的项目ID")
    setup: Mapped[str | None] = mapped_column(Text, doc="运行测试所需的前置条件或设置", nullable=True)
    step: Mapped[str | None] = mapped_column(Text, doc="执行测试用例的步骤", nullable=True)
    topo: Mapped[str | None] = mapped_column(Text, doc="测试所需的网络拓扑", nullable=True)

    # 自动化相关字段
    automated: Mapped[bool] = mapped_column(Boolean, default=False, doc="标识测试用例是否已自动化")
    automation: Mapped[bool] = mapped_column(Boolean, default=False, doc="标识测试用例是否适合自动化")

    # 可选字段
    comment: Mapped[str | None] = mapped_column(Text, doc="关于测试用例的可选注释或说明", nullable=True)
    depends: Mapped[list[Any] | None] = mapped_column(JSON, doc="该用例依赖的测试用例列表", nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), doc="测试用例创建时间")
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), doc="测试用例最后更新时间"
    )
    bugs = relationship(
        "Bug", # 关联的目标模型
        secondary="bug_testcase_association", # 指定中间表的表名，用于维护多对多关系
        primaryjoin="TestCase.id == foreign(BugCases.testcase_id)", # 指定TestCase表与中间表的关联关系
        secondaryjoin="Bug.id == foreign(BugCases.bug_id)", # 指定Bug表与中间表的关联关系
        back_populates="testcases", # 双向关系 互相引用
        lazy="selectin"  # 一次性查询所有数据
    )