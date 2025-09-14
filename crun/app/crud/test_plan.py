from typing import Any, Dict, Optional, Union, List

from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.test_plan import TestPlan, TestPlanCases
from app.schemas.test_plan import TestPlanCreate, TestPlanUpdate


class CRUDTestPlan(CRUDBase[TestPlan, TestPlanCreate, TestPlanUpdate]):
    async def get_with_relations(self, db: AsyncSession, *, id: int) -> Optional[TestPlan]:
        """获取测试计划及其关联数据"""
        stmt = select(TestPlan).where(TestPlan.id == id).options(
            selectinload(TestPlan.owner),
            selectinload(TestPlan.cases)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_with_cases(
        self, db: AsyncSession, *, obj_in: TestPlanCreate
    ) -> TestPlan:
        """创建测试计划并关联测试用例"""
        # 创建测试计划
        db_obj = TestPlan(**obj_in.model_dump(exclude={'case_indexs'}))
        db.add(db_obj)
        await db.flush()  # 获取ID
        
        # 如果提供了测试用例索引，创建关联关系
        if obj_in.case_indexs:
            for case_index in obj_in.case_indexs:
                test_plan_case = TestPlanCases(
                    project_id=db_obj.project_id,
                    plan_id=db_obj.id,
                    case_index=case_index
                )
                db.add(test_plan_case)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_with_cases(
        self, db: AsyncSession, *, db_obj: TestPlan, obj_in: Union[TestPlanUpdate, Dict[str, Any]]
    ) -> TestPlan:
        """更新测试计划并管理关联的测试用例"""
        if isinstance(obj_in, dict):
            data = obj_in
        else:
            data = obj_in.model_dump()

        case_indexs = data.pop('case_indexs', None)

        # 更新基本字段
        for field, value in data.items():
            setattr(db_obj, field, value)

        # 如果提供了case_indexs，更新关联关系
        if case_indexs is not None:
            # 删除现有的关联关系
            await db.execute(
                delete(TestPlanCases).where(TestPlanCases.plan_id == db_obj.id)
            )
            
            # 创建新的关联关系
            for case_index in case_indexs:
                test_plan_case = TestPlanCases(
                    project_id=db_obj.project_id,
                    plan_id=db_obj.id,
                    case_index=case_index
                )
                db.add(test_plan_case)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    def _extra_filters(self, query, kwargs):
        """额外的查询过滤条件"""
        name = kwargs.pop('name', None)
        project_id = kwargs.pop('project_id', None)
        owner_id = kwargs.pop('owner_id', None)
        status = kwargs.pop('status', None)
        
        if name:
            query = query.where(TestPlan.name.contains(name))
        if project_id:
            query = query.where(TestPlan.project_id == project_id)
        if owner_id:
            query = query.where(TestPlan.owner_id == owner_id)
        if status is not None:
            query = query.where(TestPlan.status == status)
            
        return query


test_plan = CRUDTestPlan(TestPlan)