from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.schemas import CaseRecord


class TaskRecordStatus(str, Enum):
    Created = 'Created'
    Running = 'Running'
    Passed = 'Passed'
    Failed = 'Failed'
    Canceled = 'Canceled'
    Error = 'Error'
    Unknown = ''


class TaskRecordBase(BaseModel):
    project_id: int
    testplan_id: int | None = None
    failed_continue: int | None = None
    status: TaskRecordStatus | None = None
    branch: str | None = None
    image: str | None = None
    repo: str | None = None


class TaskRecordCreate(TaskRecordBase):
    task_id: int
    agent_id: int | None = None
    creater: str | None = 'System'
    container_id: str | None = None
    logs: str | None = None
    env_vars: List[dict] | None = None


class TaskRecordUpdate(TaskRecordBase):
    project_id: int | None = None


class TaskRunOut(BaseModel):
    id: int
    creater: str | None = 'System'
    task_id: int
    container_id: str | None = None
    agent_id: int | None = None


class TaskRecord(TaskRecordBase):
    id: int
    task_id: int
    passed: int | None = None
    failed: int | None = None
    total: int | None = None
    created_at: datetime | None = None
    case_records: List[CaseRecord] | None = None


class TaskRecordList(BaseModel):
    list: List[TaskRecord]
    total: int


class ContainerStatus(str, Enum):
    Running = 'Running'
    Stopped = 'Stopped'
    Failed = 'Failed'
    Succeeded = 'Succeeded'
    Unknown = 'Unknown'


class ContainerStopData(BaseModel):
    status: Optional[ContainerStatus] = None
    container_id: str
    timestamp: str
