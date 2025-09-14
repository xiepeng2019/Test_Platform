import json
from typing import Tuple, List
import asyncio

import aiohttp
from loguru import logger
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clients.agent_client import agent_client
from app.core import deps
from app.crud import tasks as crud
from app.crud import task_record as crud_task_record
from app.models import (
    User,
    Project as ProjectModel,
    TestTask as TestTaskModel,
    TestTaskRecord as TestTaskRecordModel,
    TestCaseRecord,
)
from app.schemas import (
    TestTaskUpdate,
    TaskStatus,
    TestTask,
    TestTaskCreate,
    TaskRecordCreate,
    TaskRecordUpdate,
    TestTaskListItem,
    TaskRecordStatus,
    ServerOnTaskRun,
)


class TaskService():
    """ TestTask Service"""

    def __init__(self):
        ...

    async def log_stream(self, request: Request, queue: asyncio.Queue):
        while not await request.is_disconnected():
            line = await queue.get()
            yield f"{line}\r\n"

    async def build_task_record_create(
        self,
        task: TestTaskModel,
        project: ProjectModel,
        db: AsyncSession = Depends(deps.get_db)
    ) -> TestTaskRecordModel:
        task_record: TestTaskRecordModel = await crud_task_record.create(
            db=db,
            project_id=task.project_id,
            obj_in=TaskRecordCreate(
                project_id=task.project_id,
                testplan_id=task.testplan_id,
                task_id=task.id,
                failed_continue=task.failed_continue,
                status=TaskRecordStatus.Created,
                container_id='',
                branch=project.branch,
                image="python:3.10",
                repo=project.git_repo,
                agent_id=0,  # TODO 目前只有一个 agent
                env_vars=task.config.env_vars if task.config else None,
            )
        )
        return task_record

    async def update_status(
        self,
        db: AsyncSession,
        task: TestTaskModel,
        task_status: TaskStatus,
        task_record: TestTaskRecordModel,
        record_status: TaskRecordStatus,
    ):
        await crud.update_status(db, task, task_status)
        await crud_task_record.update(
            db=db,
            db_obj=task_record,
            obj_in=TaskRecordUpdate(
                status=record_status
            )
        )

    async def update_status_running(self, db: AsyncSession, task: TestTaskModel, task_record: TestTaskRecordModel):
        await self.update_status(
            db=db,
            task=task,
            task_status=TaskStatus.Running,
            task_record=task_record,
            record_status=TaskRecordStatus.Running,
        )

    async def update_status_error(
        self,
        db: AsyncSession,
        task: TestTaskModel,
        task_record: TestTaskRecordModel,
    ):
        await self.update_status(
            db=db,
            task=task,
            task_status=TaskStatus.Error,
            task_record=task_record,
            record_status=TaskRecordStatus.Error,
        )

    async def run(
        self,
        task: TestTaskModel,
        project: ProjectModel,
        db: AsyncSession = Depends(deps.get_db),
    ) -> TestTaskRecordModel:
        if not task.cases:
            raise HTTPException(status_code=400, detail="测试任务中必须包含至少一个测试用例")

        task_record: TestTaskRecordModel = await self.build_task_record_create(
            task=task,
            project=project,
            db=db,
        )

        # 批量创建test_case_record
        case_records = [
            TestCaseRecord(**{
                'task_record_id': task_record.id,
                'case_index': case.index,
                'start_time': None,
                'end_time': None,
                'duration': None,
            })
            for case in task.cases
        ]
        db.add_all(case_records)
        await db.flush()

        try:
            await agent_client.heartbeat()
            test_env = ServerOnTaskRun.model_validate(task.server) if task.server else None
            server = test_env.model_dump_json() if test_env else {}
            data = await agent_client.run_task(
                job_id=task_record.id,
                repo=str(task_record.repo),
                cases_index=[case.index for case in task.cases],
                image=str(task_record.image),
                branch=str(task_record.branch),
                env_vars=task.config.env_vars if task.config else None,
                server=json.loads(server) if isinstance(server, str) else server,
            )
            if data['status'] != 'created':
                await self.update_status_error(db=db, task=task, task_record=task_record)
                raise HTTPException(status_code=500, detail="Task run failed")
            await self.update_status_running(db=db, task=task, task_record=task_record)
            return await crud_task_record.get_last_record(db=db, task_id=task.id)
        except asyncio.CancelledError as e:
            logger.info('Task was cancelled from cancelled error')
            await self.update_status_error(db=db, task=task, task_record=task_record)
            raise HTTPException(status_code=500, detail="Task was cancelled")
        except asyncio.TimeoutError as e:
            logger.error('Agent timeout from timeout error')
            await self.update_status_error(db=db, task=task, task_record=task_record)
            raise HTTPException(status_code=500, detail="Agent timeout")
        except aiohttp.ClientError as e:
            logger.error('Agent is not running from client error')
            await self.update_status_error(db=db, task=task, task_record=task_record)
            raise HTTPException(status_code=500, detail="Agent is not running") from e
        except HTTPException as e:
            logger.exception(e)
            logger.error('Task run failed from http exception')
            await self.update_status_error(db=db, task=task, task_record=task_record)
            raise e
        except BaseException as e:
            logger.exception(e)
            logger.error('Task run failed from base exception')
            await self.update_status_error(db=db, task=task, task_record=task_record)
            raise HTTPException(status_code=500, detail="Task run failed") from e

    async def get(
        self,
        task: TestTaskModel
    ) -> TestTask:
        data = TestTask.model_validate(task, from_attributes=True)
        data.cases_index = [case.index for case in task.cases]
        return data

    async def list(
        self,
        query_params: dict,
        db: AsyncSession = Depends(deps.get_db),
    ) -> Tuple[List[TestTaskListItem], int]:
        """List datas """
        logger.info(f'list_data, query_params={query_params}')
        datas = await crud.get_multi(db, **query_params)
        total = await crud.count(db, **query_params)
        schema_datas = [TestTaskListItem.model_validate(data) for data in datas]
        return schema_datas, total

    async def create(
        self,
        data_in: TestTaskCreate,
        db: AsyncSession,
        user: User,
        project_id: int,
    ) -> TestTask:
        """Create new data """
        task = await crud.create(db, data_in, user, project_id)
        return task

    async def update(
        self,
        db: AsyncSession,
        project_id: int,
        user: User,
        task_id: int,
        data_in: TestTaskUpdate,
    ):
        data = await crud.get(db=db, id=task_id, project_id=project_id)
        if not data:
            raise HTTPException(status_code=404, detail="Task not found")

        # 鉴权
        if str(data.owner_id) != str(user.id):
            raise HTTPException(status_code=403, detail="请联系任务责任人修改！")

        # 更新数据
        data = await crud.update(db=db, task=data, data_in=data_in)
        return data

    async def delete(self, db: AsyncSession, task: TestTask):
        return await crud.remove(db=db, id=task.id)


def get_task_service() -> TaskService:
    return TaskService()