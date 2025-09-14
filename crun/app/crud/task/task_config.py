from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models import TaskConfig
from app.schemas import TaskConfigCreate, TaskConfigUpdate


class CRUDTaskConfig(CRUDBase[TaskConfig, TaskConfigCreate, TaskConfigUpdate]):
    async def get_by_id(self, db: AsyncSession, *, id: int) -> Optional[TaskConfig]:
        result = await db.execute(select(TaskConfig).filter(TaskConfig.id == id))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, project_id: int, obj_in: TaskConfigCreate, owner_id: int) -> TaskConfig:
        """Create a new task config with owner_id support."""
        db_obj = TaskConfig(
            project_id=project_id,
            owner_id=owner_id,
            **obj_in.model_dump(exclude_unset=True)
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


task_configs = CRUDTaskConfig(TaskConfig)