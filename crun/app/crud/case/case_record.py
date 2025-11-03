from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models import TestTaskRecord, TestCaseRecord
from app.schemas import CaseResultCreate, CaseRecordUpdate


class CRUDCaseRecord(CRUDBase[TestCaseRecord, CaseResultCreate, CaseRecordUpdate]):
    async def get_by_task_id(self, db: AsyncSession, *, task_id: int32) -> List[TestCaseRecord]:
        """根据任务ID获取测试用例记录"""
        result = await db.execute(
            select(self.model).where(self.model.task_record_id == task_id)
        )
        return list(result.scalars().all())

    async def get_by_task_id_and_case_index(self, db: AsyncSession, *, task_id: int32, case_index: str
    ) -> TestCaseRecord | None:
        """根据任务ID和用例索引获取测试用例记录"""
        result = await db.execute(
            select(self.model).where(
                self.model.task_record_id == task_id,
                self.model.case_index == case_index
            )
        )
        return result.scalars().first() # 返回第一个匹配的记录

    async def update_case_record(self, db: AsyncSession, record_id: str, data_in: CaseResultCreate,) -> TestCaseRecord:
        """更新测试用例记录"""
        tr = await db.get(TestTaskRecord, record_id)
        if not tr:
            raise HTTPException(status_code=404, detail="Task record not found")
        cr = await db.execute(
            select(self.model).where(
                self.model.task_record_id == tr.id,
                self.model.case_index == data_in.result.case_index
            )
        )
        case_record = cr.scalars().first()
        if not case_record:
            raise HTTPException(status_code=404, detail="Case record not found")

        case_record.result = data_in.result.result
        case_record.start_time = data_in.result.start_time
        case_record.end_time = data_in.result.end_time
        case_record.duration = data_in.result.duration
        await db.commit()
        await db.refresh(case_record)
        return case_record


crud_case_record = CRUDCaseRecord(TestCaseRecord)