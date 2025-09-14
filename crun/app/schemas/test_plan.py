from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.schemas import TestCase, UserRead


class TestPlanBase(BaseModel):
    name: str
    project_id: int
    stage: Optional[int] = None
    owner_id: str
    status: Optional[int] = None


class TestPlanCreate(TestPlanBase):
    case_indexs: Optional[List[str]] = None  # 创建时关联的测试用例索引列表


class TestPlanUpdate(BaseModel):
    name: Optional[str] = None
    project_id: Optional[int] = None
    stage: Optional[int] = None
    owner_id: Optional[str] = None
    status: Optional[int] = None
    case_indexs: Optional[List[str]] = None  # 更新时关联的测试用例索引列表


class TestPlanInDBBase(TestPlanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TestPlan(TestPlanInDBBase):
    pass


class TestPlanWithRelations(TestPlanInDBBase):
    owner: Optional[UserRead] = None
    cases: Optional[List[TestCase]] = None


class TestPlanQueryParams(BaseModel):
    name: Optional[str] = None
    owner_id: Optional[str] = None
    status: Optional[int] = None


class TestPlanList(BaseModel):
    list: List[TestPlan]
    total: int
