from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import deps
from app.schemas.reports.report import (TestReportQueryParams,
                                        TestReportCreate,
                                        TestReportUpdate,
                                        TestReportDelete,
                                        TestReportList
                                        )
from app.crud.report.reports import report as crud

# 路由实例化
report_router = APIRouter(prefix="/api/reports")

# 返回模型response_model=BugList
@report_router.get("", response_model=TestReportList, operation_id='queryTestReport')
async def query_test_report(
    # Depends 依赖
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
    page: int = 1,
    pageSize: int = 50,
    query: TestReportQueryParams = Depends() # 查询参数依赖
) -> Any:
    """查询测试报告"""
    skip = (page - 1) * pageSize
    # model_dump 将将模型实例转换为python字典，过滤掉模型中未被显示赋值的字段
    query_params = query.model_dump(exclude_unset=True)
    query_params["project_id"] = project_id
    query_params["skip"] = skip
    query_params["limit"] = pageSize
    # hasattr 判断对象是否有指定的名称的属性
    # 协程：等待获取到查询到的数据后在执行后面的内容
    reposts_list = await crud.get_multi(db=db, **query_params)
    total = await crud.count(db=db, **query_params)
    return {
        "list": reposts_list,
        "total": total
    }


@report_router.post("", response_model=TestReportCreate)
async def create_test_report(obj_in: TestReportCreate, db: AsyncSession = Depends(deps.get_db)) -> Any:
    """创建测试报告"""
    # CRUD：数据库操作
    return await crud.create(db=db, obj_in=obj_in, project_id=1)

@report_router.put("/{id}", response_model=TestReportList)
async def update_test_report(id: int,  obj_in: TestReportUpdate, db: AsyncSession = Depends(deps.get_db)) -> Any:
    """更新测试报告"""
    bug = await crud.get(db=db, id=id)
    if not bug:
        raise HTTPException(status_code=404, detail="Test Report Not Found")
    return await crud.update(db=db, db_obj=bug, obj_in=obj_in)


@report_router.delete("/{id}", response_model=TestReportDelete)
async def delete_test_report(id: int, db: AsyncSession = Depends(deps.get_db)) -> Any:
    """删除测试报告"""
    bug = await crud.get(db=db, id=id)
    if not bug:
        raise HTTPException(status_code=404, detail="Test Report Not Found")
    await crud.remove(db=db, id=id)
    return TestReportDelete(id=id, message="Delete Success")
