from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.crud import case_node as crud
from app.crud import project as crud_project
from app.crud import cases as crud_case
from app.core import deps
from app.schemas import (
    TestCaseNode,
    TestCaseUpdate,
    TestCaseNodeCreate,
    TestCaseNodeUpdate,
    TestCaseNodeList,
)

router = APIRouter(prefix="/api/case_node")
source = 'Case Node'


@router.get("", response_model=TestCaseNodeList, operation_id='listTestCaseNode')
async def read_datas(
    db: AsyncSession = Depends(deps.get_db),
    project_id: Optional[int] = Depends(deps.current_project_id),
    parent_id: Optional[int] = None,
    name: Optional[str] = None
) -> Any:
    """获取用例节点列表"""
    query_params = {
        "parent_id": parent_id,
        "project_id": project_id,
        "name": name,
    }
    datas = await crud.get_multi(db, **query_params)
    total = await crud.count(db, **query_params)
    return {
        "list": datas,
        "total": total,
    }


@router.post("", response_model=TestCaseNode, operation_id='createTestCaseNode')
async def create(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    data_in: TestCaseNodeCreate,
    project_id: int = Depends(deps.current_project_id),
) -> Any:
    """创建用例节点"""
    project = await crud_project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project not found")
    data = await crud.create(db=db, project_id=project_id, obj_in=data_in.model_dump())
    return data


@router.get("/tree", response_model=list, operation_id='listTestCaseNodeTree')
async def read_tree(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
) -> Any:
    """获取用例节点树"""
    tree = await crud.get_tree(db=db, project_id=project_id)
    return tree


@router.get("/tree/cases", response_model=list, operation_id='listTestCaseNodeTreeCases')
async def read_tree_cases(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
) -> Any:
    """获取用例节点树中的用例"""
    async def get_cases(nodes):
        for node in nodes:
            if not node['children']:
                cases = []
                cases = await crud_case.get_by_node_id(db=db, node_id=node['key'])
                node['children'] = [
                    {
                        "key": case.index,
                        "title": case.name,
                        "index": case.index,
                        "children": [],
                    } for case in cases
                ]
            else:
                await get_cases(node['children'])
        return

    tree = await crud.get_tree(db=db, project_id=project_id)
    await get_cases(tree)
    return tree


@router.patch("/{id}", response_model=TestCaseNode, operation_id='updateTestCaseNode')
async def update(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    data_in: TestCaseNodeUpdate,
) -> Any:
    """更新用例节点"""
    data = await crud.get(db=db, id=id)
    if not data:
        raise HTTPException(status_code=404, detail=f"{source} not found")
    logger.info(data_in)
    data = await crud.update(db=db, db_obj=data, obj_in=TestCaseUpdate(**data_in.model_dump()))
    return data


@router.get("/{id}", response_model=TestCaseNode, operation_id='getTestCaseNode')
async def read(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    id: int,
) -> Any:
    """获取用例节点"""
    data = await crud.get(db=db, id=id)
    if not data:
        raise HTTPException(status_code=404, detail=f"{source} not found")
    return data


@router.delete("/{id}", response_model=TestCaseNode, operation_id='deleteTestCaseNode')
async def delete(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    id: int,
) -> Any:
    """删除用例节点"""
    data = await crud.get(db=db, id=id)
    if not data:
        raise HTTPException(status_code=404, detail=f"{source} not found")
    data = await crud.remove(db=db, id=id)
    return data
