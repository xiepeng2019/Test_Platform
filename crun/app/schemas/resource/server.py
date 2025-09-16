from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import ConfigDict, Field
from pydantic import BaseModel
from app.schemas.user import UserSearch


class BoardBase(BaseModel):
    # link_type: str = Field(..., description="连接类型")
    ip: str = Field(..., description="IP地址")
    port: int | None = Field(None, description="端口")
    username: str | None = Field(None, description="用户名")
    password: str | None = Field(None, description="密码")

    model_config = ConfigDict(from_attributes=True)


class BoardCreate(BoardBase):
    pass


class ServerStatus(str, Enum):
    IDLE = 'IDLE'
    IN_USE = 'IN_USE'
    MAINTENANCE = 'MAINTENANCE'
    ERROR = 'ERROR'
    UNKNOWN = 'UNKNOWN'


class LinkType(str, Enum):
    VIRTUAL = 'virtual'
    SSH = 'ssh'
    TELNET = 'telnet'


class PsuBase(BaseModel):
    ip: str = Field(..., description="IP地址", pattern=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    outlet: int | None = Field(None, description="Outlet端口")
    username: str | None = Field(None, description="用户名")
    password: str | None = Field(None, description="密码")

    model_config = ConfigDict(from_attributes=True)


class ServerBase(BaseModel):
    name: str = Field(..., description="服务器名称")
    project_id: int = Field(..., description="所属项目ID")
    status: ServerStatus | None = Field(ServerStatus.IDLE, description="环境状态")
    ip: str = Field(..., description="IP地址", pattern=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    sn: str | None = Field(None, description="序列号", pattern=r"^[A-Za-z0-9]+$")


class ServerCreate(BaseModel):
    """Schema for creating a new server"""
    name: str = Field(..., description="服务器名称")
    ip:  str = Field(..., description="IP地址", pattern=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    sn:  str = Field(..., description="序列号", pattern=r"^[A-Za-z0-9]+$")
    bmc_ip:  str = Field(..., description="BMC IP地址", pattern=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    bmc_username:  str = Field(..., description="BMC 用户名")
    bmc_password:  str = Field(..., description="BMC 密码")
    port:  int = Field(..., description="服务端口", gt=0, lt=65536)
    username:  str = Field(..., description="用户名")
    password:  str = Field(..., description="密码")
    status: ServerStatus | None = Field(ServerStatus.IDLE, description="环境状态")
    link_type: LinkType | None = Field(LinkType.VIRTUAL, description="连接类型")
    boards: List[BoardCreate] = Field([], description="板卡列表")
    psu_1: PsuBase | None = Field(None, description="PDU-1")
    psu_2: PsuBase | None = Field(None, description="PDU-2")


class ServerUpdate(ServerCreate):
    """Schema for updating a test server"""
    ...


class ServerOptions(BaseModel):
    """Schema for retrieving a test server options"""
    id: int = Field(..., description="资源ID")
    name: str = Field(..., description="环境名称")


class ServerInTask(BaseModel):
    name: str = Field(..., description="服务器名称")
    ip: str = Field(..., description="IP地址")
    sn: str | None = Field(None, description="序列号")
    id: int = Field(..., description="资源ID")
    bmc_ip: Optional[str] = Field(..., description="BMC IP地址")
    bmc_username: Optional[str] = Field(..., description="BMC 用户名")
    port: Optional[int] = Field(..., description="服务端口")
    username: Optional[str] = Field(..., description="用户名")

    model_config = ConfigDict(from_attributes=True)


class Server(ServerBase):
    """Schema for retrieving a test server"""
    id: int = Field(..., description="资源ID")
    owner_id: int = Field(..., description="创建人ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    owner: Optional[UserSearch] = Field(None, description="责任人")
    bmc_ip: Optional[str] = Field(..., description="BMC IP地址")
    bmc_username: Optional[str] = Field(..., description="BMC 用户名")
    bmc_password: Optional[str] = Field(..., description="BMC 密码")
    bmc_web_username: Optional[str] = Field(..., description="BMC Web 用户名")
    bmc_web_password: Optional[str] = Field(..., description="BMC Web 密码")
    port: Optional[int] = Field(..., description="服务端口")
    username: Optional[str] = Field(..., description="用户名")
    password: Optional[str] = Field(..., description="密码")
    boards: List[BoardCreate] = Field([], description="板卡列表")
    link_type: LinkType | None = Field(LinkType.VIRTUAL, description="连接类型")
    psu_1: PsuBase | None = Field(None, description="PDU-1")
    psu_2: PsuBase | None = Field(None, description="PDU-2")

    model_config = ConfigDict(from_attributes=True)


class ServerOnTaskRun(BaseModel):
    name: str = Field(..., description="环境名称")
    ip: str = Field(..., description="IP地址")
    sn: str | None = Field(None, description="序列号")
    username: Optional[str] = Field(..., description="用户名")
    password: Optional[str] = Field(..., description="密码")
    bmc_ip: Optional[str] = Field(..., description="BMC IP地址")
    bmc_username: Optional[str] = Field(..., description="BMC 用户名")
    bmc_password: Optional[str] = Field(..., description="BMC 密码")
    bmc_web_username: Optional[str] = Field(..., description="BMC Web 用户名")
    bmc_web_password: Optional[str] = Field(..., description="BMC Web 密码")
    port: Optional[int] = Field(..., description="服务端口")
    boards: List[BoardCreate] = Field([], description="板卡列表")
    link_type: LinkType | None = Field(LinkType.VIRTUAL, description="连接类型")
    psu_1: PsuBase | None = Field(None, description="PDU-1")
    psu_2: PsuBase | None = Field(None, description="PDU-2")

    model_config = ConfigDict(from_attributes=True)


class ServerQueryParams(BaseModel):
    name: Optional[str] = None
    owner: Optional[str] = None
    sn: Optional[str] = None
    ip: Optional[str] = None


class ServerList(BaseModel):
    list: List[Server] = []
    total: int = 0