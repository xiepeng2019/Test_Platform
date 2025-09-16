from datetime import datetime
from typing import List
from pydantic import BaseModel, validator



class TestReportsBase(BaseModel):
    """测试报告基类"""
    id: int                               # 测试报告ID
    report_no: str                        # 报告编号
    title: str                            # 报告标题
    project_name: str                     # 项目名称
    project_version: str                  # 项目版本
    test_type: str                        # 测试类型（功能/性能/安全）
    start_time: datetime | None = None    # 测试开始时间
    end_time: datetime | None = None      # 测试结束时间
    tester: str | None = None             # 测试人员
    reviewer: str | None = None           # 审核人员
    scope: str | None = None              # 测试范围
    purpose: str | None = None            # 测试目的
    conclusion: int | None = None         # 测试结论
    suggestions:int | None = None         # 改进建议
    test_method: str | None = None        # 测试方法
    create_at: datetime | None = None     # 创建时间
    update_at: datetime | None = None     # 创建时间

    # 自定义验证器，在数据被解析到模型字段之前，对字段值进行校验、转换或处理，确保数据符合预期格式或业务规则。
    @validator("project_name")
    def name_cannot_be_empty(cls, v):
        if ' ' in v:
            raise ValueError('项目名称不允许包含空格')
        return v

    # pre=True 表示该验证器在 Pydantic 自身的验证逻辑之前执行；always=True 表示无论 create_at 字段是否有值，该验证器都会执行
    # 如果 v 不为 None（即显式设置了创建时间），则直接返回该值
    @validator('create_at', pre=True, always=True)
    def set_create_time(cls, v):
        if v is None:
            return datetime.now()  # 设置默认值
        return v


class TestReportCreate(BaseModel):
    """创建测试报告"""
    report_no: str                          # 报告编号
    title: str                              # 报告标题
    project_name: str                       # 项目名称
    project_version: str                    # 项目版本
    test_type: str                          # 测试类型（功能/性能/安全）
    start_time: datetime | None = None      # 测试开始时间
    end_time: datetime | None = None        # 测试结束时间

    # Pydantic 模型支持与 ORM（对象关系映射）对象的交互
    class Config:
        orm_mode = True

class TestReportUpdate(TestReportsBase):
    """更新测试报告"""

    class Config:
        orm_mode = True

class TestReportDelete(BaseModel):
    message: str

class TestReportRead(TestReportsBase):
    id: int                 # 测试报告ID
    total_cases: int
    passed_cases: int
    failed_cases: int
    blocked_cases: int
    pass_rate: float
    created_at: datetime
    updated_at: datetime
    is_published: bool


class EnvironmentBase(BaseModel):
    """环境信息"""
    name: str
    hardware: str
    software: str
    database: str


class TestReportQueryParams(BaseModel):
    """查询模型"""
    report_id: int | None = None # 报告id
    report_no: str | None = None # 报告编号
    title: str | None = None        # 报告标题
    project_name: str | None = None# 项目名称
    project_version: str | None = None # 项目版本


class TestReportList(BaseModel):
    list: List[TestReportsBase]
    total: int