from typing import Tuple, List

from loguru import logger
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    TestTaskRecord as TestTaskRecordModel,
)
from app.schemas import (
    ContainerStatus,
    ContainerStopData,
    TaskRecord,
    TaskRecordStatus,
    CaseRecord,
    CaseRecordStatus,
    CaseResultCreate,
    TaskStatus
)
from app.crud import (
    crud_case_record,
    task_record as crud_task_record,
    tasks as crud_task
)


class TaskRecordService():
    """任务记录服务"""

    def __init__(self):
        ...

    async def get_task_record(
        self,
        db: AsyncSession,
        task_id: int,
    ) -> TestTaskRecordModel:
        """获取任务记录"""
        task_record = await crud_task_record.get_last_record(db=db, task_id=task_id)
        if not task_record:
            raise HTTPException(status_code=404, detail="Task record not found")
        return task_record

    async def list(
        self,
        db: AsyncSession,
        task_id: int,
    ) -> Tuple[List[TaskRecord], int]:
        """获取任务记录列表"""
        datas = await crud_task_record.get_multi(db=db, task_id=task_id, limit=999)
        if not datas:
            raise HTTPException(status_code=404, detail="Task record not found")
        task_records = []
        for record in datas:
            record_info = TaskRecord.model_validate(record, from_attributes=True)
            record_info.passed = 0
            record_info.failed = 0
            record_info.case_records = []
            case_records = await crud_case_record.get_by_task_id(db=db, task_id=record.id)
            for case_record in case_records:
                record_info.case_records.append(CaseRecord.model_validate(case_record, from_attributes=True))
                if not case_record.result:
                    continue
                if case_record.result.upper() == 'PASSED':
                    record_info.passed += 1
                elif case_record.result.upper() == 'FAILED':
                    record_info.failed += 1
            task_records.insert(0, record_info)
            record_info.total = len(record_info.case_records)
        return task_records, len(datas)


    async def update_case_record(
        self,
        db: AsyncSession,
        data_in: CaseResultCreate,
    ) -> CaseRecord:
        """更新测试用例执行记录"""
        logger.info(f'update_task_record, record_id={data_in.record_id}, data_in={data_in}')
        case_record = await crud_case_record.update_case_record(db=db, record_id=data_in.record_id, data_in=data_in)
        return CaseRecord.model_validate(case_record, from_attributes=True)


    async def container_stop(
        self,
        db: AsyncSession,
        job_id: int,
        data_in: ContainerStopData,
    ) -> None:
        """停止任务容器"""
        logger.info(f'container_stop, data_in={data_in}')
        task = await crud_task_record.get_task_by_id(db=db, job_id=job_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        task_record = await crud_task_record.get(db, job_id)
        if not task_record:
            raise HTTPException(status_code=404, detail="Task record not found")

        # 容器状态转换为任务状态
        record_status = TaskRecordStatus.Error
        task_status = TaskStatus.Error
        if data_in.status == ContainerStatus.Failed:
            record_status = TaskRecordStatus.Failed
            task_status = TaskStatus.Failed
        elif data_in.status == ContainerStatus.Stopped:
            record_status = TaskRecordStatus.Canceled
            task_status = TaskStatus.Canceled
        elif data_in.status == ContainerStatus.Succeeded:
            case_records = await crud_case_record.get_multi(db=db, task_record_id=task_record.id)
            status_set = set([case_record.result if case_record.result else None for case_record in case_records])
            
            # 根据用例结果集合判断最终任务状态
            # 1. 如果结果集合中只包含PASSED，则任务状态为Passed（空值不算Passed）
            # 2. 如果结果集合中只包含PASSED和FAILED，则任务状态为Failed
            # 3. 其他情况（包含ERROR、空值或空集合），任务状态为Error
            if status_set == {CaseRecordStatus.Passed}:
                record_status = TaskRecordStatus.Passed
                task_status = TaskStatus.Passed
            elif status_set and status_set <= {CaseRecordStatus.Passed, CaseRecordStatus.Failed}:  # 非空且只包含PASSED/FAILED
                record_status = TaskRecordStatus.Failed
                task_status = TaskStatus.Failed
            else:
                record_status = TaskRecordStatus.Error
                task_status = TaskStatus.Error

        await crud_task.update_status(db, task, task_status)
        await crud_task_record.update(
            db=db,
            db_obj=task_record,
            obj_in={'status': record_status}
        )


def get_task_record_service() -> TaskRecordService:
    """获取任务记录服务"""
    return TaskRecordService()
