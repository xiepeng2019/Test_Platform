import uuid
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, Header, Path, HTTPException, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from app.core.database import async_session
from app.config.config import get_settings
from app.models import User
from app.models import TestTask
from app.crud import tasks as crud_tasks


class CustomSQLAlchemyUserDatabase(SQLAlchemyUserDatabase):
    async def get_by_union_id(self, union_id: str) -> User | None:
        statement = select(self.user_table).where(self.user_table.union_id == union_id)
        return await self._get_user(statement)

    async def search(self, q: str):
        statement = select(self.user_table).where(self.user_table.name.ilike(f'%{q}%'))
        response = await self.session.execute(statement)
        return [u[0] for u in response.all()]


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield CustomSQLAlchemyUserDatabase(session, User)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    pass


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=get_settings().SECRET_KEY, lifetime_seconds=get_settings().JWT_EXPIRATION_TIME)


bearer_transport = BearerTransport(tokenUrl="api/auth/jwt/login")
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)


def current_project_id(
    request: Request,
    x_project_id: Optional[int] = Header(0, description="Project ID (optional)")
):
    if not hasattr(request.state, 'project_id'):
        return 0
    return request.state.project_id


async def get_task_by_id(
    id: int = Path(..., description="The ID of the task"),
    project_id: int = Depends(current_project_id),
    db: AsyncSession = Depends(get_db),
) -> TestTask:
    task = await crud_tasks.get(db=db, id=id, project_id=project_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
