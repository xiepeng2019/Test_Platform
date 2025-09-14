from typing import Any

from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.orm import Base


class TestCaseRecord(Base):
    __tablename__ = "test_case_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, doc="测试任务记录的唯一标识")
    task_record_id: Mapped[int] = mapped_column(Integer, index=True, doc="关联的测试任务记录ID")
    case_index: Mapped[str] = mapped_column(String(100), index=True, doc="测试用例的索引")
    result: Mapped[str | None] = mapped_column(String(100), doc="测试用例的结果", nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, doc="测试用例的开始时间", nullable=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, doc="测试用例的结束时间", nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer, doc="测试用例的运行时间", nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), doc="任务创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), doc="任务最后更新时间"
    )
