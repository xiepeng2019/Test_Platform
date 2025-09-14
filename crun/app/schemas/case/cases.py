from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class TestCaseBase(BaseModel):
    index: str
    name: str
    objective: str
    priority: str

    # 自动化相关字段
    automated: int = 0
    automation: int = 0

    # 可选字段处理
    comment: Optional[str] = None
    depends: Optional[list] = None
    node_id: Optional[int] = 0
    module: Optional[str] = ''
    test_type: Optional[str] = ''
    expected: Optional[str] = ''
    setup:Optional[str]= ''
    step: Optional[str] = ''
    topo: Optional[str] = ''


class TestCase(TestCaseBase):
    model_config = ConfigDict(from_attributes=True)
    
    project_id: int
    id: int
    created_at: datetime
    updated_at: datetime


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseUpdate(TestCaseBase):
    index: Optional[str] = None
    name: Optional[str] = None
    objective: Optional[str] = None
    priority: Optional[str] = None

    # 自动化相关字段
    automated: Optional[int] = None
    automation: Optional[int] = None

class TestCaseList(BaseModel):
    list: List[TestCase]
    total: int


# 用例文件上传
class BatchTestCaseCreate(TestCaseCreate):
    project_id: int


class TestCaseFileValidateError(BaseModel):
    sheet: str
    type: str  # e.g. "missing_columns", "empty_sheet"
    errors: List[str]


class BatchTestCaseFileValidateError(BaseModel):
    detail: List[TestCaseFileValidateError]


class ValidateSuccessResponse(BaseModel):
    message: str
    valid_sheets: List[str]
    warnings: List[TestCaseFileValidateError] = []


class GenericErrorResponse(BaseModel):
    detail: str
