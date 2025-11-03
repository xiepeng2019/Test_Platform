from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import deps
from app.schemas import CaseResultCreate, CaseRecord
from app.services import TaskRecordService, get_task_record_service


router = APIRouter(prefix="/api/test_task")


@router.post('/case_result', response_model=CaseRecord)
async def case_result(
    *,
    data_in: CaseResultCreate,
    db: AsyncSession = Depends(deps.get_db),
    service: TaskRecordService = Depends(get_task_record_service),
) -> CaseRecord:
    """创建或更新测试用例执行记录"""
    return await service.update_case_record(db, data_in)
