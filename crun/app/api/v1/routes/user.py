import uuid
from typing import List
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, Depends, File
from fastapi_users import FastAPIUsers
from fastapi_users import BaseUserManager

from app.core.deps import auth_backend, get_user_manager, fastapi_users
from app.schemas import UserCreate, UserRead, UserSearch, UserUpdate, UpdateUserAvatar
from app.models import User
from .mock_permissions import permissions


router = APIRouter()
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/api/auth/jwt",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/auth",
    tags=["auth"],
)

@router.get("/api/users/me", response_model=UserRead, operation_id='getUserInfo')
async def users_me(user: User = Depends(fastapi_users.current_user(active=True))):
    # 1. 初始化一个空的权限列表
    permission_list = []

    # 2. 在这里添加您的自定义逻辑来构造权限
    # 例如，给所有用户添加看板的读权限
    permission_list.append({"resource": "dashboard", "actions": ["read"]})

    # 例如，如果用户是管理员，则添加额外的权限
    # (这假设您的 User 模型中有 'is_superuser' 或类似字段)
    # if user.is_superuser:
    #     permission_list.append({"resource": "admin_panel", "actions": ["read", "write"]})

    # 3. 将构造好的权限列表赋值给 user 对象的 permission 字段
    # 注意：这不会将更改保存到数据库，仅用于本次响应
    user.permissions = permissions

    # 4. 返回修改后的 user 对象
    return user


@router.get('/api/users/search', response_model=List[UserSearch], tags=['users'], operation_id='searchUser')
async def users_search(
    q: str = '',
    user_manager: BaseUserManager[User, uuid.UUID] = Depends(get_user_manager)
):
    return await user_manager.user_db.search(q)


@router.post("/api/users/me/avatar", response_model=UpdateUserAvatar, tags=["users"], operation_id='uploadAvatar')
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(fastapi_users.current_user(active=True)),
    user_manager: BaseUserManager[User, uuid.UUID] = Depends(get_user_manager)
):
    media_path = Path("/media/avatars")
    media_path.mkdir(parents=True, exist_ok=True)

    file_extension = Path(file.filename).suffix
    file_name = f"{uuid.uuid4()}{file_extension}"
    file_path = media_path / file_name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    avatar_url = f"/media/avatars/{file_name}"
    user.avatar = avatar_url
    await user_manager.user_db.update(user, {"avatar": avatar_url})

    return {"avatar": avatar_url}


router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/users",
    tags=["users"],
)