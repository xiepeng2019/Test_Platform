from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import deps
from app.schemas import (
    TestPlanCreate,
    TestPlanUpdate,
    TestPlan,
    TestPlanWithRelations,
    TestPlanList,
    TestPlanQueryParams,
)
from app.services import get_test_plan_service, TestPlanService

router = APIRouter(prefix="/api/test-plans")


@router.get("", response_model=TestPlanList)
async def read_datas(
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
    page: int = 1,
    pageSize: int = 10,
    query: TestPlanQueryParams = Depends(),
    service: TestPlanService = Depends(get_test_plan_service),
) -> Any:
    """获取测试计划列表"""
    skip = (page - 1) * pageSize
    query_params = query.model_dump(exclude_unset=True)
    query_params["project_id"] = project_id
    query_params["skip"] = skip
    query_params["limit"] = pageSize

    test_plans, total = await service.list(db=db, query_params=query_params)
    return TestPlanList(
        list=test_plans,
        total=total,
    )


@router.post("")
async def create_data(
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """创建测试计划并关联测试用例"""
    return {}


@router.get("/{id}", response_model=TestPlanWithRelations)
async def read_data(
    id: int,
    db: AsyncSession = Depends(deps.get_db),
    service: TestPlanService = Depends(get_test_plan_service),
) -> Any:
    """根据ID获取测试计划及其关联数据"""
    return {

    }

