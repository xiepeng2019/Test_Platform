from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.schemas import UserSearch


class EnvVar(BaseModel):
    name: str
    value: str


class TaskConfigBase(BaseModel):
    name: str
    description: Optional[str] = None
    env_vars: Optional[List[EnvVar]] = None

    model_config = ConfigDict(from_attributes=True)


class TaskConfigCreate(TaskConfigBase):
    pass


class TaskConfigUpdate(TaskConfigBase):
    pass


class TaskConfig(TaskConfigBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskConfigListItem(TaskConfig):
    owner: UserSearch


class TaskConfigList(BaseModel):
    list: List[TaskConfigListItem]
    total: int


class TaskConfigQueryParams(BaseModel):
    name: Optional[str] = None


class TaskConfigOptions(BaseModel):
    name: str
    id: int