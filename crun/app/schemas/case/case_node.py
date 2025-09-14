from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class TestCaseNodeBase(BaseModel):
    name: str
    comment: Optional[str] = None
    parent_id: Optional[int] = None
    creater: Optional[str] = 'Linlin'


class TestCaseNode(TestCaseNodeBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

class TestCaseNodeCreate(BaseModel):
    name: str
    comment: Optional[str] = None
    parent_id: Optional[int] = None
    creater: Optional[str] = 'Linlin'


class TestCaseNodeUpdate(BaseModel):
    name: Optional[str] = None
    comment: Optional[str] = None
    parent_id: Optional[int] = None


class TestCaseNodeList(BaseModel):
    list: List[TestCaseNode]
    total: int


class TestCaseNodeTreeItem(BaseModel):
    key: str
    title: str
    children: Optional[List['TestCaseNodeTreeItem']] = []
    case_count: Optional[int] = 0


class TestCaseNodeTreeItemOfTask(TestCaseNodeTreeItem):
    selected_case_count: Optional[int] = 0
    children: Optional[List['TestCaseNodeTreeItemOfTask']] = []
