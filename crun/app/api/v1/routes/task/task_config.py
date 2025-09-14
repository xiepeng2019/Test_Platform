from typing import List
from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import deps
from app.crud import task_configs as crud
from app.models import User
from app.schemas import (
    TaskConfig,
    TaskConfigCreate,
    TaskConfigOptions,
    TaskConfigUpdate,
    TaskConfigList,
    TaskConfigListItem,
    TaskConfigQueryParams
)

router = APIRouter(prefix="/api/task_config")


@router.get("", response_model=TaskConfigList, operation_id="listTaskConfigs")
async def list_task_configs(
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
    user: User = Depends(deps.fastapi_users.current_user(active=True)),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=0, le=1000),
    query_params: TaskConfigQueryParams = Depends()
):
    """获取任务配置列表"""
    filters = {
        "project_id": project_id,
        **query_params.model_dump(exclude_none=True)
    }
    task_configs_list = await crud.get_multi(db, skip=skip, limit=limit, **filters)
    total = await crud.count(db, **filters)
    # Convert TaskConfig objects to TaskConfigListItem objects
    list_items = [TaskConfigListItem(**task_config.__dict__) for task_config in task_configs_list]
    return TaskConfigList(list=list_items, total=total)


@router.post("", response_model=TaskConfig, operation_id="createTaskConfig")
async def create_task_config(
    task_config_in: TaskConfigCreate,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
    user: User = Depends(deps.fastapi_users.current_user(active=True))
):
    """创建新的任务配置"""
    task_config = await crud.create(db, project_id=project_id, obj_in=task_config_in, owner_id=user.id)
    return task_config


@router.get("/options", response_model=List[TaskConfigOptions], operation_id='listTaskConfigOptions')
async def read_data_options(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id)
):
    f"""
    Retrieve task config options.
    """
    return await crud.get_options(db, project_id=project_id)


@router.get("/{task_config_id}", response_model=TaskConfig, operation_id="getTaskConfig")
async def get_task_config(
    task_config_id: int = Path(..., description="任务配置ID"),
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
    user: User = Depends(deps.fastapi_users.current_user(active=True))
):
    """获取任务配置详情"""
    task_config = await crud.get(db, task_config_id, project_id=project_id)
    if not task_config:
        raise HTTPException(status_code=404, detail="任务配置不存在")
    return task_config


@router.patch("/{task_config_id}", response_model=TaskConfig, operation_id="updateTaskConfig")
async def update_task_config(
    task_config_in: TaskConfigUpdate,
    task_config_id: int = Path(..., description="任务配置ID"),
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
    user: User = Depends(deps.fastapi_users.current_user(active=True))
):
    """更新任务配置"""
    task_config = await crud.get(db, task_config_id, project_id=project_id)
    if not task_config:
        raise HTTPException(status_code=404, detail="任务配置不存在")
    task_config = await crud.update(db, db_obj=task_config, obj_in=task_config_in)
    return task_config


@router.delete("/{task_config_id}", response_model=TaskConfig, operation_id="deleteTaskConfig")
async def delete_task_config(
    task_config_id: int = Path(..., description="任务配置ID"),
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
    user: User = Depends(deps.fastapi_users.current_user(active=True))
):
    """删除任务配置"""
    task_config = await crud.get(db, task_config_id, project_id=project_id)
    if not task_config:
        raise HTTPException(status_code=404, detail="任务配置不存在")
    task_config = await crud.remove(db, id=task_config_id)
    return task_config