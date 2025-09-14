from typing import Optional

from loguru import logger
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.task import task as TaskModels
from app.models import user as UserModels
from app.schemas.task import task as TaskSchemas


class CRUDTestTask(CRUDBase[TaskModels.TestTask, TaskSchemas.TestTaskCreate, TaskSchemas.TestTaskUpdate]):
    def _extra_filters(self, query, querys):
        owner = querys.pop('owner', None)
        if owner:
            logger.info(f'_extra_filters, owner={owner}')
            query = query.join(
                UserModels.User,
                (self.model.owner_id == UserModels.User.id)
            ).where(UserModels.User.id == owner)
        return query


    async def get_by_id(self, db: AsyncSession, *, id: int) -> Optional[TaskModels.TestTask]:
        result = await db.execute(select(TaskModels.TestTask).filter(TaskModels.TestTask.id == id))
        return result.scalars().first()

    async def update_status(self, db: AsyncSession, task: TaskModels.TestTask, status: TaskSchemas.TaskStatus):
        """更新任务状态 """
        task.status = status
        db.add(task)
        await db.commit()
        await db.refresh(task)

    async def create(
        self,
        db: AsyncSession,
        data_in: TaskSchemas.TestTaskCreate,
        user: UserModels.User,
        project_id: int,
    ) -> TaskSchemas.TestTask:
        """Create new data """
        task_obj = TaskModels.TestTask(**{
            **data_in.model_dump(exclude={"cases", "project_id", "owner", "creater"}),
            'project_id': project_id,
            'owner_id': user.id,
        })
        db.add(task_obj)
        await db.flush()

        # 更新关联表
        if data_in.cases:
            case_links = [
                TaskModels.TestTaskCases(**{
                    "project_id": project_id,
                    "task_id": task_obj.id,
                    "case_index": case_index,
                })
                for case_index in data_in.cases
            ]
            db.add_all(case_links)

        await db.commit()
        await db.refresh(task_obj)

        # 数据处理
        task = TaskSchemas.TestTask.model_validate(task_obj, from_attributes=True)
        task.cases_index = [case.index for case in task_obj.cases]
        return task

    async def update(self, db: AsyncSession, task: TaskModels.TestTask, data_in: TaskSchemas.TestTaskUpdate):
        """Update data """
        await super().update(
            db,
            db_obj=task,
            obj_in=data_in.model_dump(
                exclude_unset=True,
                exclude={
                    "cases",
                    "project_id",
                    "owner",
                    "creater"
                }
            )
        )

        await db.execute(
            delete(TaskModels.TestTaskCases).where(TaskModels.TestTaskCases.task_id == task.id)
        )

        if data_in.cases:
            db.add_all([
                TaskModels.TestTaskCases(
                    project_id=task.project_id,
                    task_id=task.id,
                    case_index=case_index,
                )
                for case_index in data_in.cases
            ])

        await db.commit()
        await db.refresh(task)
        return task

tasks = CRUDTestTask(TaskModels.TestTask)
