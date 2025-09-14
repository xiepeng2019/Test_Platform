from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.orm import Base
from app.models.user import User
from app.models.project import Project


class Pdu(Base):
    """Represents a pdu resource."""
    __tablename__ = "pdu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, doc="资源的唯一标识")
    ip: Mapped[str] = mapped_column(String(50), index=True, doc="IP地址")
    username: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="用户名")
    password: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="密码")
    outlet: Mapped[int | None] = mapped_column(Integer, nullable=True, doc="Outlet端口")

    server_psu_1: Mapped["Server"] = relationship(
        "Server",
        back_populates="psu_1",
        uselist=False,
        primaryjoin="Pdu.id == foreign(Server.psu_1_id)"
    )

    server_psu_2: Mapped["Server"] = relationship(
        "Server",
        back_populates="psu_2",
        uselist=False,
        primaryjoin="Pdu.id == foreign(Server.psu_2_id)"
    )


class Board(Base):
    """Represents a board resource."""
    __tablename__ = "board"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, doc="资源的唯一标识")
    ip: Mapped[str] = mapped_column(String(50), index=True, doc="IP地址")
    port: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="端口")
    username: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="用户名")
    password: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="密码")

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), doc="创建时间")
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), doc="更新时间"
    )

    server_id: Mapped[int | None] = mapped_column(Integer, nullable=True, doc="关联的服务器ID")
    server: Mapped["Server"] = relationship(
        "Server",
        primaryjoin="foreign(Board.server_id) == Server.id",
        lazy="joined",
    )


class Server(Base):
    """Represents a test server resource."""
    __tablename__ = "server"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, doc="资源的唯一标识")
    status: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="环境状态")

    name: Mapped[str] = mapped_column(String(50), index=True, doc="环境名称")
    ip: Mapped[str] = mapped_column(String(50), index=True, doc="IP地址")
    sn: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True, doc="序列号")
    port: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="端口")
    username: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="用户名")
    password: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="密码")

    bmc_ip: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="BMC IP地址")
    bmc_username: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="BMC 用户名")
    bmc_password: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="BMC 密码")
    bmc_web_username: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="BMC Web 用户名")
    bmc_web_password: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="BMC Web 密码")
    link_type: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="板卡连接类型")

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), doc="创建时间")
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), doc="更新时间"
    )

    owner_id: Mapped[int] = mapped_column(Integer, index=True, doc="创建人ID")
    owner: Mapped[User] = relationship(
        "User",
        primaryjoin="foreign(Server.owner_id) == User.id",
        lazy="joined",
    )

    project_id: Mapped[int] = mapped_column(Integer, index=True, doc="所属项目ID")
    project: Mapped["Project"] = relationship(
        "Project",
        primaryjoin="foreign(Server.project_id) == Project.id",
        lazy="joined",
    )

    psu_1_id: Mapped[int | None] = mapped_column(Integer, nullable=True, doc="PDU-1 ID")
    psu_1: Mapped[Pdu] = relationship(
        "Pdu",
        back_populates="server_psu_1",
        primaryjoin="foreign(Server.psu_1_id) == Pdu.id",
        lazy="joined",
        uselist=False,  # 1 by 1
        single_parent=True,
        cascade="all, delete-orphan"
    )

    psu_2_id: Mapped[int | None] = mapped_column(Integer, nullable=True, doc="PDU-2 ID")
    psu_2: Mapped[Pdu] = relationship(
        "Pdu",
        back_populates="server_psu_2",
        primaryjoin="foreign(Server.psu_2_id) == Pdu.id",
        uselist=False,
        single_parent=True,
        lazy="joined",
        cascade="all, delete-orphan"
    )

    boards: Mapped[list[Board]] = relationship(
        "Board",
        primaryjoin="foreign(Board.server_id) == Server.id",
        lazy="selectin",  # 先查server，再 IN 查board
        cascade="all, delete-orphan"
    )