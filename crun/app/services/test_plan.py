from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.test_plan import test_plan as crud_test_plan
from app.schemas import TestPlan, TestPlanCreate, TestPlanUpdate, TestPlanWithRelations


class TestPlanService:
    def __init__(self):
        self.crud = crud_test_plan

    async def list(
        self, db: AsyncSession, *, query_params: Dict[str, Any]
    ) -> tuple[List[TestPlan], int]:
        """获取测试计划列表"""
        datas = await self.crud.get_multi(db, **query_params)
        total = await self.crud.count(db, **query_params)
        schema_datas = [TestPlan.model_validate(data) for data in datas]
        return schema_datas, total

    async def create(
        self, db: AsyncSession, *, data_in: TestPlanCreate
    ) -> TestPlan:
        """创建测试计划"""
        model_obj = await self.crud.create_with_cases(db, obj_in=data_in)
        return TestPlan.model_validate(model_obj)

    async def get(
        self, db: AsyncSession, *, id: int) -> Optional[TestPlanWithRelations]:
        """根据ID获取测试计划"""
        model_obj = await self.crud.get_with_relations(db, id=id)
        return TestPlanWithRelations.model_validate(model_obj) if model_obj else None

    async def update(
        self, db: AsyncSession, *, id: int, data_in: TestPlanUpdate
    ) -> Optional[TestPlan]:
        """更新测试计划"""
        db_obj = await self.crud.get_with_relations(db, id=id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Test plan not found")
        updated_obj = await self.crud.update_with_cases(db, db_obj=db_obj, obj_in=data_in)
        return TestPlan.model_validate(updated_obj)

    async def delete(self, db: AsyncSession, *, id: int) -> Optional[TestPlan]:
        """删除测试计划"""
        db_obj = await self.crud.get(db, id=id)
        if not db_obj:
            return None
        deleted_obj = await self.crud.remove(db, id=id)
        return TestPlan.model_validate(deleted_obj) if deleted_obj else None


def get_test_plan_service() -> TestPlanService:
    return TestPlanService()