import asyncio
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.models import TestTask
from app.models import user as UserModels
from app.schemas.task import task as TaskSchemas
from app.schemas.task import task_record as TaskRecordSchemas
from app.schemas.case import case_node as CaseNodeSchemas
from app.core.clients.agent_client import agent_client
from app.crud import project as crud_project
from app.crud import case_node as crud_case_node
from app.core.clients.agent_client import agent_client
from app.core import deps
from app.services import TaskService, get_task_service
from app.services import TaskRecordService, get_task_record_service


router = APIRouter(prefix="/api/test_task")


@router.get("", response_model=TaskSchemas.TestTaskList, operation_id='listTestTask')
async def list(
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
    page: int = 1,
    pageSize: int = 10,
    query: TaskSchemas.TestTaskQueryParams = Depends(),
    service: TaskService = Depends(get_task_service),
) -> Any:
    """获取任务列表"""
    skip = (page - 1) * pageSize
    query_params = query.model_dump(exclude_unset=True)
    query_params["project_id"] = project_id
    query_params["skip"] = skip
    query_params["limit"] = pageSize

    tasks, total = await service.list(db=db, query_params=query_params)
    return TaskSchemas.TestTaskList(
        list=tasks,
        total=total,
    )


@router.post("", response_model=TaskSchemas.TestTask, operation_id='createTestTask')
async def create(
    *,
    db: AsyncSession = Depends(deps.get_db),
    data_in: TaskSchemas.TestTaskCreate,
    service: TaskService = Depends(get_task_service),
    user: UserModels.User = Depends(deps.fastapi_users.current_user(active=True)),
    project_id: int = Depends(deps.current_project_id),
) -> Any:
    """创建新任务"""
    return await service.create(
        db=db,
        data_in=data_in,
        user=user,
        project_id=project_id,
    )


@router.patch("/{id}", response_model=TaskSchemas.TestTask, operation_id='updateTestTask')
async def update(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    data_in: TaskSchemas.TestTaskUpdate,
    service: TaskService = Depends(get_task_service),
    project_id: int = Depends(deps.current_project_id),
    user: UserModels.User = Depends(deps.fastapi_users.current_user(active=True)),
) -> Any:
    """更新任务"""
    return await service.update(db, project_id, user, id, data_in)


@router.get("/{id}", response_model=TaskSchemas.TestTask, operation_id='getTestTask')
async def get(
    *,
    task: TestTask = Depends(deps.get_task_by_id),
    service: TaskService = Depends(get_task_service),
) -> Any:
    """获取任务"""
    return await service.get(task)


@router.delete("/{id}", response_model=TaskSchemas.TestTask, operation_id='deleteTestTask')
async def delete(
    *,
    db: AsyncSession = Depends(deps.get_db),
    task: TestTask = Depends(deps.get_task_by_id),
    service: TaskService = Depends(get_task_service),
) -> Any:
    """删除任务"""
    delete_obj = await service.delete(db, task)
    return TaskSchemas.TestTask.model_validate(delete_obj)


@router.post("/{id}/run", response_model=TaskRecordSchemas.TaskRunOut, operation_id='runTestTask')
async def run(
    *,
    db: AsyncSession = Depends(deps.get_db),
    task: TestTask = Depends(deps.get_task_by_id),
    service: TaskService = Depends(get_task_service),
    project_id: int = Depends(deps.current_project_id),
) -> Any:
    """运行任务"""
    project = await crud_project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return await service.run(
        task=task,
        project=project,
        db=db,
    )

@router.get("/{id}/tree", response_model=List[CaseNodeSchemas.TestCaseNodeTreeItemOfTask], operation_id='getTestTaskTree')
async def tree(
    *, 
    db: AsyncSession = Depends(deps.get_db), 
    task: TestTask = Depends(deps.get_task_by_id), project_id: int = Depends(deps.current_project_id),
) -> Any:
    """获取任务树"""
    return await crud_case_node.get_tree_with_task_selected(
        db=db,
        project_id=project_id,
        task_id=task.id
    )


@router.get("/{id}/log/stream", operation_id='getTestTaskLogSSE')
async def logs_sse(
    request: Request,  # FastAPI 封装的请求对象，用于检测客户端连接状态
    db: AsyncSession = Depends(deps.get_db),  # 异步数据库会话，通过依赖注入获取
    task: TestTask = Depends(deps.get_task_by_id),  # 测试任务对象，通过路径参数`id`查询得到
    task_service: TaskService = Depends(get_task_service),  # 任务相关的业务逻辑服务
    record_service: TaskRecordService = Depends(get_task_record_service),  # 任务记录相关的业务逻辑服务
):
    """获取任务日志流"""
    task_record = await record_service.get_task_record(db, task_id=task.id) # 查询任务记录，根据任务ID获取任务记录对象。
    queue = asyncio.Queue() # 创建一个异步队列，用于在任务记录ID和代理客户端之间传递日志消息。
    # task_queues[str(task_record.id)] = queue

    asyncio.create_task(agent_client.start_ws_to_agent(str(task_record.id), queue)) # 启动一个异步任务，将任务记录ID和队列传递给代理客户端，开始从代理接收日志消息。
    return StreamingResponse(
        task_service.log_stream(request, queue), media_type="text/event-stream"   # SSE 协议的 MIME 类型，告诉客户端这是一个持续的事件流，需要保持连接并持续接收数据。
    )


@router.get("/{id}/records", response_model=TaskRecordSchemas.TaskRecordList, operation_id='listTestTaskRecord')
async def records(
    *,
    task: TestTask = Depends(deps.get_task_by_id), # 测试任务对象，通过路径参数`id`查询得到
    db: AsyncSession = Depends(deps.get_db), # 异步数据库会话，通过依赖注入获取
    record_service: TaskRecordService = Depends(get_task_record_service), # 任务记录相关的业务逻辑服务
) -> Any:
    """获取任务记录列表"""
    await asyncio.sleep(1)
    datas, total = await record_service.list(db, task_id=task.id) # 查询任务记录，根据任务ID获取任务记录列表。
    return TaskRecordSchemas.TaskRecordList(
        list=datas,
        total=total,
    )