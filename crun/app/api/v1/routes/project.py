from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi_users import FastAPIUsers
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import project as crud
from app.core import deps
from app.models import User
from app.schemas import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectOptions,
    ProjectList,
)


router = APIRouter(prefix="/api/projects")
source = 'Project'
"""FastAPI用户认证"""
fastapi_users = FastAPIUsers[User, int](
    deps.get_user_manager,
    [deps.auth_backend],
)


@router.get("", response_model=ProjectList, operation_id='listProject')
async def read_datas(
    db: AsyncSession = Depends(deps.get_db),
    page: int = 1,
    pageSize: int = 10,
    name: Optional[str] = None,
    git_repo: Optional[str] = None,
    branch: Optional[str] = None,
    owners: Optional[int] = None,
) -> Any:
    f"""
    Retrieve {source}.
    """
    skip = (page - 1) * pageSize
    query_params = {
        "name": name,
        "git_repo": git_repo,
        "branch": branch,
        "owners": owners,
    }
    datas = await crud.get_multi(db, skip=skip, limit=pageSize, **query_params)
    total = await crud.count(db, **query_params)

    return {
        "list": datas,
        "total": total,
    }


@router.post("", response_model=Project, operation_id='createProject')
async def create_data(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    data_in: ProjectCreate,
    _: User = Depends(fastapi_users.current_user(active=True)),
) -> Any:
    f"""
    Create new {source}.
    """
    response = await crud.create(db=db, obj_in=data_in)
    return response


@router.get("/options", response_model=List[ProjectOptions], operation_id='listProjectOptions')
async def read_data_options(
    *,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    f"""
    Retrieve {source} options.
    """
    return await crud.get_options(db)


@router.patch("/{id}", response_model=Project, operation_id='updateProject')
async def update_data(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    data_in: ProjectUpdate,
) -> Any:
    f"""
    Update an {source}.
    """
    data = await crud.get(db=db, id=id)
    if not data:
        raise HTTPException(status_code=404, detail=f"{source} not found")
    return await crud.update(db=db, db_obj=data, obj_in=data_in)


@router.get("/{id}", operation_id='getProject')
async def read_data(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    id: int,
) -> Any:
    f"""
    Get {source} by ID.
    """
    data = await crud.get(db=db, id=id)
    if not data:
        raise HTTPException(status_code=404, detail=f"{source} not found")
    return data


@router.delete("/{id}", response_model=Project, operation_id='deleteProject')
async def delete_data(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    id: int,
) -> Any:
    f"""
    Delete an {source}.
    """
    data = await crud.get(db=db, id=id)
    if not data:
        raise HTTPException(status_code=404, detail=f"{source} not found")
    return await crud.remove(db=db, id=id)
