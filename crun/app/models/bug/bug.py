from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.orm import Base


class BugCases(Base):
    """bug and case associatio"""
    __tablename__ = "bug_testcase_association"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bug_id: Mapped[int] = mapped_column(Integer, index=True)
    testcase_id: Mapped[int] = mapped_column(Integer, index=True)

    # 逻辑外键关联 TestCase，没有外键约束，使用 foreign() 明确外键引用
    cases = relationship(
        "TestCase",
        # primaryjoin多表关联时的连接条件
        primaryjoin="BugCases.testcase_id == foreign(TestCase.id)",
        # 控制关联数据的加载时机，
        lazy="selectin",
        # 指定表的关联关系是1对1 还是1对多，还是多对多，True:1对多, False: 1对1
        uselist=False
    )

    task = relationship(
        "Bug",
        primaryjoin="BugCases.bug_id == foreign(Bug.id)",
        lazy="selectin",
    )


# 模型名称，继承基类
class Bug(Base):
    """BUG table"""
    __tablename__ = "bug"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, doc="测试计划唯一标识")
    title: Mapped[str] = mapped_column(String(100), nullable=False, doc="标题") # 不允许为空，True: 允许为空
    status: Mapped[str] = mapped_column(String(100), doc="状态")
    severity: Mapped[str] = mapped_column(String(100), doc="严重级别")
    steps: Mapped[str] = mapped_column(String(100), doc="复现步骤")
    resolved: Mapped[bool] = mapped_column(default=False, doc="是否解决")
    resolution_time: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True, doc="解决时间")
    assignee_id: Mapped[str] = mapped_column(String(100), doc="指派人ID")
    submitter_id: Mapped[str] = mapped_column(String(100), doc="提交人")
    closed: Mapped[bool] = mapped_column(default=False, doc="是否关闭")
    closing_time: Mapped[DateTime | None] = mapped_column(DateTime, server_default=func.now(), doc="关闭时间")
    project_id: Mapped[int] = mapped_column(Integer, index=True, doc="该计划所属的项目ID")
    create_time: Mapped[DateTime | None] = mapped_column(DateTime, server_default=func.now(), doc="创建时间")
    case_index: Mapped[list[str] | None] = mapped_column(String(100), nullable=True, doc="关联用例列表索引")
    create_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), doc="创建时间")
    update_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), doc="任务最后更新时间")

    testcases = relationship(
        "TestCase", # 关联的目标模型
        secondary="bug_testcase_association", # 指定中间表的表名，用于维护多对多关系
        primaryjoin="Bug.id == foreign(BugCases.bug_id)", # 指定TestCase表与中间表的关联关系
        secondaryjoin="TestCase.id == foreign(BugCases.testcase_id)",  # 指定Bug表与中间表的关联关系
        back_populates="bugs",
        lazy="selectin"  # 一次性查询所有数据
    )
