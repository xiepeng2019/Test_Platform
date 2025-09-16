from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import deps
from app.schemas.bug.bug import (BugList, BugCreate, BugUpdate, BugQueryParams, BugDelete)
from app.schemas.bug import bug as bug_schemas
from app.crud.bug.bug import bug as crud

# 路由实例化
bug_router = APIRouter(prefix="/api/bugs")

# 返回模型response_model=BugList
@bug_router.get("", response_model=BugList)
async def query_bug(
    # Depends 依赖
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
    page: int = 1,
    pageSize: int = 10,
    query: BugQueryParams = Depends()
) -> Any:
    """查询BUG"""
    skip = (page - 1) * pageSize
    # model_dump 将将模型实例转换为python字典，过滤掉模型中未被显示赋值的字段
    query_params = query.model_dump(exclude_unset=True)
    query_params["project_id"] = project_id
    query_params["skip"] = skip
    query_params["limit"] = pageSize
    # hasattr 判断对象是否有指定的名称的属性
    if hasattr(query, "status") and query.status:
        query_params["status"] = query.status.value  # 处理枚举类型的状态
    # 协程：等待获取到查询到的数据后在执行后面的内容
    bugs = await crud.get_multi(db=db, **query_params)
    total = await crud.count(db=db, **query_params)
    return {
        "list": bugs,
        "total": total
    }


@bug_router.post("", response_model=bug_schemas.Bug)
async def create_bug(obj_in: BugCreate, db: AsyncSession = Depends(deps.get_db)) -> Any:
    """创建BUG"""
    # CRUD：数据库操作
    return await crud.create_bug(db=db, obj_in=obj_in, project_id=1)


@bug_router.put("/{id}", response_model=bug_schemas.Bug)
async def update_bug(id: int,  obj_in: BugUpdate, db: AsyncSession = Depends(deps.get_db)) -> Any:
    """更新BUG"""
    bug = await crud.get(db=db, id=id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return await crud.update(db=db, db_obj=bug, obj_in=obj_in)


@bug_router.delete("/{id}", response_model=BugDelete)
async def delete_bug(id: int, db: AsyncSession = Depends(deps.get_db)) -> Any:
    """删除BUG"""
    bug = await crud.get(db=db, id=id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    await crud.remove(db=db, id=id)
    return BugDelete(id=id, message="Delete Success")
