from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CaseRecordStatus(str, Enum):
    Passed = 'passed'
    Failed = 'failed'
    Skipped = 'skipped'
    XFailed = 'xfailed'
    XPassed = 'xpassed'
    Error = 'error'


class CaseRecordBase(BaseModel):
    task_record_id: int
    case_index: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    result: Optional[CaseRecordStatus] = None


class CaseRecord(CaseRecordBase):
    id: int

    class Config:
        from_attributes = True


class CaseRecordCreateItem(BaseModel):
    case_node: str
    result: str
    case_index: str
    start_time: datetime
    end_time: datetime
    duration: int


class CaseResultCreate(BaseModel):
    record_id: str
    result: CaseRecordCreateItem


class CaseRecordUpdate(BaseModel):
    ...