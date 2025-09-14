import asyncio
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import deps
from app.crud import server as crud
from app.schemas import (
    ServerCreate,
    ServerOptions,
    ServerQueryParams,
    ServerUpdate,
    Server,
    ServerList
)
from app.models import User

router = APIRouter(prefix="/api/resource/server")


@router.get("", response_model=ServerList, operation_id='listServer')
async def read_datas(
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
    page: int = 1,
    pageSize: int = 10,
    query: ServerQueryParams = Depends(),
) -> Any:
    """获取服务器列表"""
    await asyncio.sleep(1)
    skip = (page - 1) * pageSize
    query_params = query.model_dump(exclude_unset=True)
    query_params["project_id"] = project_id
    query_params["skip"] = skip
    query_params["limit"] = pageSize

    datas = await crud.get_multi(db, **query_params)
    total = await crud.count(db, **query_params)
    return ServerList(list=[Server.model_validate(data) for data in datas], total=total)


@router.post("", response_model=Server, operation_id='createServer')
async def create_data(
    server_data: ServerCreate,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
    user: User = Depends(deps.fastapi_users.current_user()),
) -> Any:
    """创建测试环境"""
    exit = await crud.check_exists(
        db=db,
        project_id=project_id,
        ip=server_data.ip,
        sn=server_data.sn,
        name=server_data.name
    )
    if exit:
        name_exit = await crud.get_by_name(db=db, project_id=project_id, name=server_data.name)
        if name_exit:
            raise HTTPException(status_code=400, detail="Server name already exists")
        ip_exit = await crud.get_by_ip(db=db, project_id=project_id, ip=server_data.ip)
        if ip_exit:
            raise HTTPException(status_code=400, detail="Server ip already exists")
        sn_exit = await crud.get_by_sn(db=db, project_id=project_id, sn=server_data.sn)
        if sn_exit:
            raise HTTPException(status_code=400, detail="Server sn already exists")
    return await crud.create(db=db, obj_in=server_data, owner_id=user.id, project_id=project_id)


@router.get("/options", response_model=List[ServerOptions], operation_id='listServerOptions')
async def read_data_options(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id)
) -> Any:
    f"""
    Retrieve server options.
    """
    return await crud.get_options(db, project_id)


@router.get("/{id}", response_model=Server, operation_id='getServer')
async def read_data(
    id: int,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
) -> Any:
    """根据ID获取服务器"""
    server = await crud.get(db=db, id=id, project_id=project_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@router.patch("/{id}", response_model=Server, operation_id='updateServer')
async def update_data(
    id: int,
    server_data: ServerUpdate,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
) -> Any:
    """更新服务器"""
    db_obj = await crud.get(db=db, id=id, project_id=project_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Server not found")
    server = await crud.update(db=db, db_obj=db_obj, obj_in=server_data)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@router.delete("/{id}", response_model=Server, operation_id='deleteServer')
async def delete_data(
    id: int,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
) -> Any:
    """删除服务器"""
    db_obj = await crud.get(db=db, id=id, project_id=project_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Server not found")
    server = await crud.remove(db=db, id=id)
    return server

