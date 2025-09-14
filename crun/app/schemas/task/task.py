from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserSearch
from app.schemas.task.task_config import TaskConfig
from app.schemas.resource.server import ServerInTask


class TaskStatus(str, Enum):
    Created = 'Created'
    Running = 'Running'
    Passed = 'Passed'
    Failed = 'Failed'
    Canceled = 'Canceled'
    Error = 'Error'


class TestTaskBase(BaseModel):
    name: str

    failed_continue: int = 0
    lark_notice: int = 0
    config_id: Optional[int] = None
    server_id: Optional[int] = None
    lark_subscribe: Optional[list] = []
    cases_index: Optional[List[str]] = []
    desc: Optional[str] = ''
    comment: Optional[str] = ''
    model_config = ConfigDict(from_attributes=True)


class TestTask(TestTaskBase):
    id: int
    owner: UserSearch
    status: Optional[TaskStatus] = None
    created_at: datetime
    updated_at: datetime


class TestTaskCreate(BaseModel):
    name: str
    failed_continue: int = 0
    lark_notice: int = 0
    config_id: Optional[int] = None
    server_id: Optional[int] = None
    lark_subscribe: Optional[list] = []
    cases: Optional[List[str]] = []
    desc: Optional[str] = ''
    comment: Optional[str] = ''


class TestTaskUpdate(TestTaskCreate):
    pass


class TestTaskQueryParams(BaseModel):
    name: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[int] = None


class TestTaskListItem(BaseModel):
    id: int
    name: str
    owner: UserSearch
    config: Optional[TaskConfig] = None
    status: Optional[TaskStatus] = None
    server: Optional[ServerInTask] = None
    failed_continue: int = 0
    lark_notice: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TestTaskList(BaseModel):
    list: List[TestTaskListItem]
    total: int


class TestTaskRun(BaseModel):
    id: int
    status: Optional[TaskStatus] = None
    created_at: datetime
    updated_at: datetime
