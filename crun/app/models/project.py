from enum import Enum as PyEnum

from sqlalchemy import Enum, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign
from sqlalchemy.sql import func, and_

from app.core.orm import Base
from app.models.user import User


class ProjectRole(PyEnum):
    OWNER = "owner"
    QA = "qa"
    DEV = "dev"


class ProjectUser(Base):
    __tablename__ = "project_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    role: Mapped[ProjectRole] = mapped_column(Enum(ProjectRole), nullable=False)

    # 逻辑外键关联 User，没有外键约束，使用 foreign() 明确外键引用
    user = relationship(
        "User",
        primaryjoin="ProjectUser.user_id == foreign(User.id)",
        lazy="selectin",
        uselist=False  # 明确表示这是单个 User 对象，不是列表
    )

    project = relationship(
        "Project",
        primaryjoin="ProjectUser.project_id == foreign(Project.id)",
        lazy="selectin",
    )


class Project(Base):
    """Represents a project, containing its metadata and related personnel."""
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, doc="项目唯一标识")
    name: Mapped[str] = mapped_column(String(255), index=True, doc="项目名称")
    git_repo: Mapped[str] = mapped_column(String(255), doc="项目关联的 Git 仓库地址")
    branch: Mapped[str] = mapped_column(String(255), doc="Git 仓库的默认分支")
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), doc="项目创建时间")
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), doc="项目最后更新时间"
    )

    owners = relationship(
        "User",
        secondary="project_user",
        primaryjoin=and_(
            id == foreign(ProjectUser.project_id),
            ProjectUser.role == ProjectRole.OWNER,
        ),
        secondaryjoin=User.id == foreign(ProjectUser.user_id),
        lazy="selectin",
        viewonly=True,
    )

    qas = relationship(
        "User",
        secondary="project_user",
        primaryjoin=and_(
            id == foreign(ProjectUser.project_id),
            ProjectUser.role == ProjectRole.QA,
        ),
        secondaryjoin=User.id == foreign(ProjectUser.user_id),
        lazy="selectin",
        viewonly=True,
    )

    devs = relationship(
        "User",
        secondary="project_user",
        primaryjoin=and_(
            id == foreign(ProjectUser.project_id),
            ProjectUser.role == ProjectRole.DEV,
        ),
        secondaryjoin=User.id == foreign(ProjectUser.user_id),
        lazy="selectin",
        viewonly=True,
    )