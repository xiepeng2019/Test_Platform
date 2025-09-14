from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import deps
from app.schemas.bug.bug import (
    Bug,
    BugCreate,
    BugUpdate,
    BugList,
    BugQueryParams,
)
from app.crud.bug.bug import bug as crud

router = APIRouter(prefix="/api/bugs")


@router.get("", response_model=BugList)
async def read_datas(
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
    page: int = 1,
    pageSize: int = 10,
    query: BugQueryParams = Depends(),
) -> Any:
    """获取测试计划列表"""
    skip = (page - 1) * pageSize
    query_params = query.model_dump(exclude_unset=True)
    query_params["project_id"] = project_id
    query_params["skip"] = skip
    query_params["limit"] = pageSize

    bugs = await crud.get_multi(db=db, **query_params)
    total = await crud.count(db=db, **query_params)
    return {
        "list": bugs,
        "total": total,
    }


@router.post("")
async def create_data(
    obj_in: BugCreate,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """创建BUG"""
    return await crud.create(db=db, obj_in=obj_in, project_id=1)


@router.get("/{id}", response_model=Bug)
async def read_data(
    id: int,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """根据ID获取测试计划及其关联数据"""
    bug = await crud.get(db=db, id=id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return bug


@router.patch("/{id}", response_model=Bug)
async def update_data(
    *,
    id: int,
    obj_in: BugUpdate,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """更新测试计划"""
    bug = await crud.get(db=db, id=id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return await crud.update(db=db, db_obj=bug, obj_in=obj_in)


@router.delete("/{id}", response_model=Bug)
async def delete_data(
    id: int,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """删除测试计划"""
    bug = await crud.get(db=db, id=id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return await crud.remove(db=db, id=id)
