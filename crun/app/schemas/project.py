from typing import List
from datetime import datetime

from pydantic import BaseModel

from app.schemas.user import UserSearch


class ProjectBase(BaseModel):
    name: str
    git_repo: str
    branch: str
    owners: List[UserSearch]
    qas: List[UserSearch] | None = []
    devs: List[UserSearch] | None = []


class ProjectCreate(ProjectBase):
    ...


class ProjectUpdate(ProjectBase):
    ...


class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ProjectList(BaseModel):
    list: List[Project]
    total: int


class ProjectOptions(BaseModel):
    name: str
    id: int