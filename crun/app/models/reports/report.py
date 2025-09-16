from app.core.orm import Base
from typing import Optional
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime
from datetime import datetime

class TestReport(Base):
    """Test Report"""
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, doc="测试报告唯一标识")
    report_no: Mapped[str] = mapped_column(String(50), unique=True, doc="报告编号")
    title: Mapped[str] = mapped_column(String(200), doc="报告标题")
    project_name: Mapped[str] = mapped_column(String(100), doc="项目名称")
    project_version: Mapped[str] = mapped_column(String(50), doc="项目版本")
    test_type: Mapped[str] = mapped_column(String(50), doc="测试类型（功能/性能/安全")
    start_time: Mapped[datetime] = mapped_column(DateTime, doc="测试开始时间")
    end_time: Mapped[datetime] = mapped_column(DateTime, doc="测试结束时间")
    tester: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, doc="测试人员")
    reviewer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, doc="审核人员")
    scope: Mapped[str] = mapped_column(String(255), nullable=True, doc="测试范围")
    purpose: Mapped[str] = mapped_column(String(255), nullable=True, doc="测试目的")
    test_method: Mapped[str] = mapped_column(String(255), nullable=True, doc="测试方法")
    total_cases: Mapped[int] = mapped_column(default=0, doc="总用例数")
    passed_cases: Mapped[int] = mapped_column(default=0, doc="通过用例数")
    failed_cases: Mapped[int] = mapped_column(default=0, doc="失败用例数")
    blocked_cases: Mapped[int] = mapped_column(default=0, doc="阻塞用例数")
    pass_rate: Mapped[float] = mapped_column(default=0.0, doc="通过率(%)")
    conclusion: Mapped[str] = mapped_column(String(255), nullable=True, doc="测试结论")
    suggestions: Mapped[Optional[str]] = mapped_column(String(255),nullable=True, doc="改进建议")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, doc="创建时间")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now, doc="更新时间")
    is_published: Mapped[bool] = mapped_column(default=False, doc="是否发布")
    project_id: Mapped[int] = mapped_column(Integer, index=True, doc="该计划所属的项目ID")
    create_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), doc="创建时间")
    update_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(),
                                                doc="任务最后更新时间")
    # 关联环境
    # environment_id: Mapped[int] = mapped_column(ForeignKey("test_environment.id"))
    # environment: Mapped["TestEnvironment"] = relationship(back_populates="reports")