from typing import Optional, List, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.dialects.mysql import insert as mysql_insert

from app.crud.base import CRUDBase
from app.models import TestCase, TestCaseNode
from app.schemas import TestCaseCreate, TestCaseUpdate


class CRUDTestCase(CRUDBase[TestCase, TestCaseCreate, TestCaseUpdate]):
    """
    TestCase的CRUD操作
    """

    async def get_by_index(self, db: AsyncSession, *, project_id: int, index: str) -> Optional[TestCase]:
        """根据项目ID和用例索引获取测试用例"""  
        result = await db.execute(select(TestCase).filter(
            TestCase.project_id == project_id,
            TestCase.index == index
        ))
        return result.scalars().first()

    async def get_all_child_nodes(self, db: AsyncSession, node_id: int) -> List[int]:
        """递归获取所有子节点ID"""
        query = select(TestCaseNode.id).where(TestCaseNode.parent_id == node_id)
        result = await db.execute(query)
        direct_child_ids = result.scalars().all()

        all_child_ids = list(direct_child_ids)
        for child_id in direct_child_ids:
            all_child_ids.extend(await self.get_all_child_nodes(db, child_id))

        return all_child_ids

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, **kwargs
    ) -> Sequence[TestCase]:
        """根据节点ID递归获取所有子节点的测试用例"""
        query = select(self.model)
        node_id = kwargs.pop('node_id', None)

        if node_id is not None:
            child_node_ids = await self.get_all_child_nodes(db, node_id)
            all_node_ids = [node_id] + child_node_ids
            query = query.where(self.model.node_id.in_(all_node_ids))

        for key, value in kwargs.items():
            if value is not None:
                query = query.where(getattr(self.model, key).like(f"%{value}%"))

        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def count(self, db: AsyncSession, **kwargs) -> int:
        """根据节点ID递归统计所有子节点的测试用例数量"""
        query = select(func.count()).select_from(self.model)
        node_id = kwargs.pop('node_id', None)

        if node_id is not None:
            child_node_ids = await self.get_all_child_nodes(db, node_id)
            all_node_ids = [node_id] + child_node_ids
            query = query.where(self.model.node_id.in_(all_node_ids))

        for key, value in kwargs.items():
            if value is not None:
                query = query.where(getattr(self.model, key).like(f"%{value}%"))

        result = await db.execute(query)
        return result.scalar_one()

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[TestCase]:
        """根据用例名称获取测试用例"""
        result = await db.execute(select(TestCase).filter(TestCase.name == name))
        return result.scalars().first()

    async def get_by_id(self, db: AsyncSession, *, id: int) -> Optional[TestCase]:
        """根据ID获取测试用例"""
        result = await db.execute(select(TestCase).filter(TestCase.id == id))
        return result.scalars().first()

    async def get_by_node_id(self, db: AsyncSession, *, node_id: int) -> Sequence[TestCase]:
        """根据节点ID获取测试用例"""
        result = await db.execute(select(TestCase).filter(TestCase.node_id == node_id))
        return result.scalars().all()

    async def create_or_update_cases(self, db: AsyncSession, cases: list[TestCaseCreate]) -> None:
        """创建或更新测试用例"""
        case_dicts = [case.model_dump() for case in cases] # model_dump将模型实例转换为字典
        stmt = mysql_insert(TestCase).values(case_dicts) # 构建插入语句

        # 构建 update 字段（排除主键 id，不更新）
        update_dict = {
            key: stmt.inserted[key]
            for key in case_dicts[0].keys()
            if key != "id"
        }

        stmt = stmt.on_duplicate_key_update(**update_dict)

        await db.execute(stmt)
        await db.commit()


cases = CRUDTestCase(TestCase)
