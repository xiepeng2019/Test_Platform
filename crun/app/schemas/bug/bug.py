from datetime import datetime
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel



class BugStatus(str, Enum):
    """
    BUG状态
    """
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class BugBase(BaseModel):
    title: str # 标题
    status: str  # 状态
    severity: str  # 严重级别
    steps: str  # 复现步骤
    resolved: bool  # 是否解决
    resolution_time: datetime | None = None  # 解决时间
    assignee_id: str | None = None  # 指派人
    submitter_id: str | None = None  # 提交人
    closed: bool  # 是否关闭
    closing_time: datetime | None = None  # 关闭时间
    creation_time: datetime  # 创建时间

    class Config:
        orm_mode = True


class Bug(BugBase):
    id: int

    class Config:
        orm_mode = True


class BugCreate(BaseModel):
    title: str # 标题
    status: str  # 状态
    severity: str  # 严重级别
    steps: str  # 复现步骤
    resolved: bool  # 是否解决
    assignee_id: Optional[str] = None  # 指派人
    submitter_id: Optional[str] = None  # 提交人
    closed: bool  # 是否关闭


class BugUpdate(BugBase):
    ...


class TestPlanQueryParams(BaseModel):
    name: Optional[str] = None
    owner_id: Optional[str] = None
    status: Optional[BugStatus] = None


class BugList(BaseModel):
    list: List[Bug]
    total: int


class BugQueryParams(BaseModel):
    title: str | None = None  # 标题
    status: str | None = None  # 状态
    severity: str | None = None  # 严重级别
    steps: str | None = None  # 复现步骤
    resolved: bool | None = None  # 是否解决
