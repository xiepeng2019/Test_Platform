from ast import TypeVar
import json
import pdb
from pydantic import BaseModel
from sqlalchemy import Row, update, func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List, Optional, Protocol, Sequence, Type, Dict, Set, Tuple, runtime_checkable

from loguru import logger

from app.crud.base import CRUDBase
from app.models import TestCase, TestCaseNode, TestTask
from app.schemas import TestCaseCreate, TestCaseUpdate
from app.schemas import TestCaseNodeTreeItem, TestCaseNodeTreeItemOfTask


@runtime_checkable
class IntConvertible(Protocol):
    def __str__(self) -> str: ...
    def __int__(self) -> int: ...


class CaseNode(dict):
    key: IntConvertible
    title: str
    children: Optional[List['CaseNode']] = []


class TreeBuilder:
    def __init__(self) -> None:
        self.model = TestCaseNode

    async def build_tree_with_case_counts(
        self,
        db: AsyncSession,
        project_id: int,
        selected_case_indexes: Optional[Set[str]] = None
    ) -> Any:
        # 获取所有节点
        nodes = await self._get_all_nodes(db, project_id)

        # 用例总数统计：{node_id -> count}
        total_case_counts = await self._get_case_counts(db)
        # 选中的用例数统计：{node_id -> count}
        selected_case_counts = (
            await self._get_selected_case_counts(db, selected_case_indexes)
            if selected_case_indexes else {}
        )

        # 构建 node 映射
        node_map = self._build_node_map(nodes)

        # 构建树结构
        root_nodes = self._build_tree_structure(nodes, node_map)

        # 递归添加 case_count 和 selected_case_count
        for root in root_nodes:
            self._accumulate_counts(root, total_case_counts, selected_case_counts)
        return root_nodes

    async def _get_all_nodes(self, db: AsyncSession, project_id: int):
        result = await db.execute(
            select(self.model).where(self.model.project_id == project_id).order_by(self.model.id)
        )
        return result.scalars().all()

    async def _get_case_counts(self, db: AsyncSession) -> Dict[int | None, int]:
        result = await db.execute(
            select(TestCase.node_id, func.count(TestCase.index)).group_by(TestCase.node_id)
        )
        return {row[0]: row[1] for row in result.all()}

    async def _get_selected_case_counts(
        self, db: AsyncSession, selected_case_indexes: Set[str]
    ) -> Dict[int, int]:
        result = await db.execute(
            select(TestCase.node_id, func.count(TestCase.index))
            .where(TestCase.index.in_(selected_case_indexes))
            .group_by(TestCase.node_id)
        )
        return {row[0]: row[1] for row in result.all()}

    def _build_node_map(self, nodes) -> Dict[int, Dict[str, Any]]:
        return {
            node.id: {
                "key": str(node.id),
                "title": node.name,
                "children": []
            } for node in nodes
        }

    def _build_tree_structure(
        self, nodes, node_map: Dict[int, Dict[str, Any]]
    ) -> List[CaseNode]:
        root_nodes = []
        for node in nodes:
            current = node_map[node.id]
            if node.parent_id and node.parent_id in node_map:
                node_map[node.parent_id]["children"].append(current)
            else:
                root_nodes.append(current)
        return root_nodes

    def _accumulate_counts(
        self,
        node: CaseNode,
        case_counts: Dict[int | None, int],
        selected_counts: Dict[int, int]
    ) -> Tuple[int, int]:
        node_id = int(node["key"])
        total = case_counts.get(node_id, 0)
        selected = selected_counts.get(node_id, 0)
        for child in node["children"]:
            child_total, child_selected = self._accumulate_counts(child, case_counts, selected_counts)
            total += child_total
            selected += child_selected
        node["case_count"] = total
        if selected:
            node["selected_case_count"] = selected
        return total, selected


class CRUDTestCaseNode(CRUDBase[TestCaseNode, TestCaseCreate, TestCaseUpdate]):
    def __init__(self, model: Type[TestCaseNode]):
        super().__init__(model)
        self.tree_builder = TreeBuilder()

    async def get(self, db: AsyncSession, id: int, project_id: int | None = None) -> Optional[TestCaseNode]:
        if not project_id:
            result = await db.execute(select(self.model).filter(self.model.id == id))
        else:
            result = await db.execute(select(self.model).filter(self.model.id == id, self.model.project_id == project_id))
        return result.scalars().first()

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[TestCaseNode]:
        """
        Remove a case node and all its children recursively.
        """
        nodes_to_delete_ids = [id]

        async def collect_children_ids(node_id: int):
            children_query = await db.execute(select(self.model.id).filter(self.model.parent_id == node_id))
            children_ids = children_query.scalars().all()
            for child_id in children_ids:
                nodes_to_delete_ids.append(child_id)
                await collect_children_ids(child_id)

        await collect_children_ids(id)

        # Update related TestCases
        await db.execute(
            update(TestCase)
            .where(TestCase.node_id.in_(nodes_to_delete_ids))
            .values(node_id=None)
        )

        # Delete all collected nodes
        obj_query = await db.execute(select(self.model).filter(self.model.id.in_(nodes_to_delete_ids)))
        objs_to_delete = obj_query.scalars().all()
        
        if not objs_to_delete:
            return None

        for obj in objs_to_delete:
            await db.delete(obj)

        await db.commit()
        
        return objs_to_delete[0]

    async def get_tree(self, db: AsyncSession, project_id: int) -> List[TestCaseNodeTreeItem]:
        tree: List[TestCaseNodeTreeItem] = await self.tree_builder.build_tree_with_case_counts(
            db=db,
            project_id=project_id,
        )
        return tree
    
    async def get_tree_with_task_selected(
        self, db: AsyncSession, project_id: int, task_id: int
    ) -> List[TestCaseNodeTreeItemOfTask]:
        # 获取任务
        task_query = await db.execute(
            select(TestTask).filter(TestTask.id == task_id, TestTask.project_id == project_id)
        )
        task = task_query.scalar_one_or_none()
        if not task:
            raise ValueError("Task not found")

        case_indexes = set([c.index for c in task.cases])
        tree_data: List[TestCaseNodeTreeItemOfTask] = await self.tree_builder.build_tree_with_case_counts(
            db=db,
            project_id=project_id,
            selected_case_indexes=case_indexes
        )
        return tree_data

    async def get_or_create_node_by_path(
        self,
        db: AsyncSession,
        project_id: int,
        path: str,
        creater: str = 'System'
    ) -> int | None:
        parts = [part for part in path.strip("/").split("/") if part]
        parent_id = 0
        node = None

        for name in parts:
            stmt = select(self.model).where(
                self.model.project_id == project_id,
                self.model.parent_id == parent_id,
                self.model.name == name
            )
            result = await db.execute(stmt)
            node = result.scalar_one_or_none()

            if not node:
                node = TestCaseNode(**{
                    "name": name,
                    "project_id": project_id,
                    "parent_id": parent_id,
                    "creater": creater
                })
                db.add(node)
                await db.flush()
            parent_id = node.id
        return node.id if node else None


case_node = CRUDTestCaseNode(TestCaseNode)
