from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel
from app.schemas.case.cases import TestCase


class BugStatus(str, Enum):
    """
    BUG状态， 枚举
    """
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class BugBase(BaseModel):
    title: str                              # 标题
    status: str                             # 状态
    severity: str                           # 严重级别
    steps: str                              # 复现步骤
    resolved: bool                          # 是否解决
    resolution_time: datetime | None = None # 解决时间
    assignee_id: str | None= None           # 指派人
    submitter_id: str | None = None         # 提交人
    closed: bool                            # 是否关闭
    closing_time: datetime | None = None    # 关闭时间
    create_time: datetime | None = None     # 创建时间
    update_time: datetime | None = None     # 更新时间


class Bug(BugBase):
    id: int
    testcases: List[TestCase]
    class Config:
        orm_mode = True


class BugCreate(BaseModel):
    title: str                          # 标题
    status: str                         # 状态
    severity: str                       # 严重级别
    steps: str                          # 复现步骤
    resolved: bool                      # 是否解决
    assignee_id: Optional[str] = None   # 指派人
    submitter_id: Optional[str] = None  # 提交人
    closed: bool                        # 是否关闭
    test_case_id: Optional[List[int]] = None  # 允许创建时不关联任何测试用例


    class Config:
        orm_mode = True


class BugUpdate(BugBase):
    class Config:
        orm_mode = True


class BugList(BaseModel):
    list: List[BugBase]
    total: int


class BugQueryParams(BaseModel):
    title: str | None = None            # 标题
    status: BugStatus | None = None     # 状态
    severity: str | None = None         # 严重级别
    steps: str | None = None            # 复现步骤
    resolved: bool | None = None        # 是否解决


class BugDelete(BaseModel):
    id: int
    message: str


