from typing import Any

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core import deps
from app.schemas import ContainerStopData
from app.crud import task_record as crud
from app.services.task_record import TaskRecordService, get_task_record_service
from app.core.clients.agent_client import agent_client


router = APIRouter(prefix="/api/test_task/record")


@router.get("/{record_id}/log/download", operation_id='getTestTaskLogFile')
async def download_log(
    db: AsyncSession = Depends(deps.get_db),
    record_id: int = Path(..., description="The ID of the task record to get"),
):
    """ Get task  record logs"""
    task_record = await crud.get(db=db, id=record_id)
    if not task_record:
        raise HTTPException(status_code=404, detail="Task record not found")
    elif not task_record.task:
        raise HTTPException(status_code=404, detail="Task not found")
    return await agent_client.download_log(task_record.task.name, task_record.id)


@router.post(
    "/{job_id}/container_stop",
    response_model=None,
    operation_id='containerStopTestTask'
)
async def container_stop_data(
    *,
    job_id: int,
    db: AsyncSession = Depends(deps.get_db),
    data: ContainerStopData,
    service: TaskRecordService = Depends(get_task_record_service),
) -> Any:
    """ Run record data by ID. """
    logger.info(f"container_stop_data, data={data}")
    await service.container_stop(db=db, job_id=job_id, data_in=data)
