from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models import TestTask, TestTaskRecord
from app.schemas import TaskRecordCreate, TaskRecordUpdate


class CRUDTaskRecord(CRUDBase[TestTaskRecord, TaskRecordCreate, TaskRecordUpdate]):
    async def get_last_record(self, db: AsyncSession, *, task_id: int) -> TestTaskRecord | None:
        result = await db.execute(
            select(self.model).where(
                self.model.task_id == task_id
            ).order_by(self.model.id.desc()).limit(1)
        )
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[TestTaskRecord]:
        query = select(self.model)
        query = self._extra_filters(query, kwargs)
        query = self._apply_filters(query, kwargs)
        result = await db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_task_by_id(
        self, db: AsyncSession, *, job_id: int
    ) -> TestTask | None:
        result = await self.get(db=db, id=job_id)
        if not result:
            return None
        task = await db.execute(select(TestTask).where(TestTask.id == result.task_id))
        return task.scalars().first()


task_record = CRUDTaskRecord(TestTaskRecord)
