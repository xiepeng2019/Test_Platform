from typing import Any, Dict, Generic, Optional, Protocol, Sequence, Type, TypeVar, Union, runtime_checkable

from pydantic import BaseModel
from loguru import logger
from sqlalchemy import RowMapping, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(index=True)
    name: Mapped[str] = mapped_column(index=True)


@runtime_checkable
class HasProjectId(Protocol):
    project_id: int


ModelType = TypeVar("ModelType", bound=Base)  # 哪一个表模型
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)  # 创建的 schemas 是哪个 
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)  # 更新的 schemas 是哪个

# Generic 用于创建泛型类（Generic Classes）。泛型允许类、函数或方法在定义时不指定具体类型，而是在使用时动态指定，从而实现代码的复用和类型安全。
# 将类型本身作为 “参数” 传递给类或函数。
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def _project_filters(self, query, project_id: int):
        """ 项目过滤条件"""
        if isinstance(self.model, HasProjectId):
            return query.filter(self.model.project_id == project_id)
        return query

    def _apply_filters(self, query, kwargs):
        """ 模糊过滤条件"""
        for key, value in kwargs.items():
            attr = getattr(self.model, key, None)
            if not attr or not value:
                continue
            query = query.where(attr.like(f"%{value}%"))
        return query

    def _extra_filters(self, query, kwargs):
        """ 额外的过滤条件，由子类实现"""
        return query

    async def get_options(self, db: AsyncSession, project_id: int | None = None) -> Sequence[RowMapping]:
        if hasattr(self.model, 'name') and hasattr(self.model, 'id'):
            query = select(self.model.name, self.model.id)
            if project_id:
                query = self._project_filters(query, project_id)
            query = query.order_by(self.model.id)
            result = await db.execute(query)
            return result.mappings().all()
        return []

    async def get(self, db: AsyncSession, id: int, project_id: Optional[int] = None) -> Optional[ModelType]:
        if project_id:
            query = select(self.model).filter(self.model.project_id == project_id)
        else:
            query = select(self.model)
        result = await db.execute(query.filter(self.model.id == id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, **kwargs
    ) -> Sequence[ModelType]:
        query = select(self.model)
        project_id = kwargs.get('project_id')
        if project_id:
            query = self._project_filters(query, project_id)
        query = self._extra_filters(query, kwargs)
        query = self._apply_filters(query, kwargs)
        result = await db.execute(query.offset(skip).limit(limit).order_by(self.model.id.desc()))
        return result.scalars().all()

    async def count(self, db: AsyncSession, **kwargs) -> int:
        query = select(func.count()).select_from(self.model)
        project_id = kwargs.get('project_id')
        if project_id:
            query = self._project_filters(query, project_id)
        query = self._extra_filters(query, kwargs)
        query = self._apply_filters(query, kwargs)
        result = await db.execute(query)
        return result.scalar_one()

    async def create(self, db: AsyncSession, *, project_id: int, obj_in: CreateSchemaType | dict) -> ModelType:
        obj_in_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump()
        logger.debug(f"Create {self.model.__name__} with data: {obj_in_data}")
        db_obj = self.model(**{
            "project_id": project_id,
            **obj_in_data
        })
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        result = await db.execute(select(self.model).filter(self.model.id == id))
        obj = result.scalars().first()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj