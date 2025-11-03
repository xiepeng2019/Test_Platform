from loguru import logger
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Board, Server, Pdu
from app.schemas import ServerCreate, ServerUpdate


class CRUDServer(CRUDBase[Server, ServerCreate, ServerUpdate]):
    """
    Server CRUD: 服务器相关操作
    """
    async def check_exists(self, db: AsyncSession, *, ip: str, sn: str, name: str, project_id: int) -> bool:
        """
        检查服务器是否存在
        """
        return await db.scalar(
            select(self.model).where(
                or_(
                    self.model.ip == ip,
                    self.model.sn == sn,
                    self.model.name == name
                ),
                self.model.project_id == project_id).limit(1)
        )

    async def get_by_name(self, db: AsyncSession, *, name: str, project_id: int) -> bool:
        """
        根据名称获取服务器
        """
        return await db.scalar(
            select(self.model).where(
                self.model.name == name,
                self.model.project_id == project_id).limit(1)
        )

    async def get_by_ip(self, db: AsyncSession, *, ip: str, project_id: int) -> Server | None:
        """
        根据IP获取服务器
        """
        return await db.scalar(
            select(self.model).where(
                self.model.ip == ip,
                self.model.project_id == project_id).limit(1)
        )

    async def get_by_sn(self, db: AsyncSession, *, sn: str, project_id: int) -> bool:
        """
        根据SN获取服务器
        """
        return await db.scalar(
            select(self.model).where(
                self.model.sn == sn,
                self.model.project_id == project_id).limit(1)
        )

    async def create(self, db: AsyncSession, *, obj_in: ServerCreate, owner_id: int, project_id: int
    ) -> Server:
        """
        创建服务器
        """
        task_obj = Server(
            **obj_in.model_dump(exclude={"owner", "boards", "psu_1", "psu_2"}), # 排除owner, boards, psu_1, psu_2字段
            owner_id=owner_id,
            project_id=project_id,
            boards=[Board(**board.model_dump()) for board in obj_in.boards], # 转换为Board模型
            psu_1=Pdu(**obj_in.psu_1.model_dump()) if obj_in.psu_1 else None, # 转换为Pdu模型
            psu_2=Pdu(**obj_in.psu_2.model_dump()) if obj_in.psu_2 else None, # 转换为Pdu模型
        )
        logger.info(f"create server {obj_in.psu_1}, {obj_in.psu_2}")
        db.add(task_obj) # 添加到数据库
        await db.commit() # 提交到数据库
        await db.refresh(task_obj) # 刷新对象   
        return task_obj # 返回创建的服务器对象

    async def update(self, db: AsyncSession, *, db_obj: Server, obj_in: ServerUpdate) -> Server:
        """
        更新服务器
        """
        # 更新服务器基本信息
        await super().update(db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True, 
        exclude={"owner", "boards", "psu_1", "psu_2" })) # 排除owner, boards, psu_1, psu_2字段

        if obj_in.boards:
            """ 更新服务器板卡信息"""
            db_obj.boards = [
                Board(**board_data.model_dump()) for board_data in obj_in.boards
            ] if obj_in.boards else []

        if obj_in.psu_1:
            """ 更新服务器PSU1信息"""
            db_obj.psu_1 = (
                Pdu(**obj_in.psu_1.model_dump()) if obj_in.psu_1 else None
            )

        if obj_in.psu_2:
            """ 更新服务器PSU2信息"""
            db_obj.psu_2 = (
                Pdu(**obj_in.psu_2.model_dump()) if obj_in.psu_2 else None
            )

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

server = CRUDServer(Server) # 实例化CRUDServer类
