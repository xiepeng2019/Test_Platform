from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.orm import Base


class Bug(Base):
    """Represents a test plan, which is a collection of test cases."""
    __tablename__ = "bug"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, doc="测试计划的唯一标识")
    title: Mapped[str] = mapped_column(String(100), doc="测试计划的名称")
    status: Mapped[str] = mapped_column(String(100), doc="状态")  # 状态
    severity: Mapped[str] = mapped_column(String(100), doc="严重级别")  # 严重级别
    steps: Mapped[str] = mapped_column(String(100), doc="复现步骤")  # 复现步骤
    resolved: Mapped[bool] = mapped_column(default=False, doc="是否解决")  # 是否解决 
    resolution_time: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True, doc="解决时间")  # 解决时间
    assignee_id: Mapped[str | None] = mapped_column(String(100), nullable=True, doc="指派人")  # 指派人
    submitter_id: Mapped[str | None] = mapped_column(String(100), nullable=True, doc="提交人")  # 提交人
    closed: Mapped[bool] = mapped_column(default=False, doc="是否关闭")  # 是否关闭
    closing_time: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True, doc="关闭时间")  # 关闭时间
    project_id: Mapped[int] = mapped_column(Integer, index=True, doc="该计划所属的项目ID")
    creation_time: Mapped[DateTime | None] = mapped_column(DateTime, server_default=func.now(), doc="创建时间")  # 创建时间
    case_indexs: Mapped[list[str] | None] = mapped_column(String(100), nullable=True, doc="关联的用例索引列表")  # 关联的用例索引列表

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), doc="创建时间")  # 创建时间
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), doc="任务最后更新时间"
    )

