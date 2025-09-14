from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Project, ProjectUser, ProjectRole
from app.schemas import ProjectCreate, ProjectUpdate


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def _extra_filters(self, query, kwargs):
        owners = kwargs.pop('owners', None)
        if owners:
            query = query.join(
                ProjectUser,
                (self.model.id == ProjectUser.project_id) & (
                    ProjectUser.role == ProjectRole.OWNER.value)
            ).where(ProjectUser.user_id == owners)
        return query

    async def create(self, db: AsyncSession, *, obj_in: ProjectCreate) -> Project:
        db_obj = self.model(**obj_in.model_dump(exclude={"owners", "qas", "devs"}))
        db.add(db_obj)
        await db.flush()

        project_users = []
        if obj_in.owners:
            project_users.extend([
                ProjectUser(project_id=db_obj.id, user_id=user.id, role=ProjectRole.OWNER)
                for user in obj_in.owners
            ])
        if obj_in.qas:
            project_users.extend([
                ProjectUser(project_id=db_obj.id, user_id=user.id, role=ProjectRole.QA)
                for user in obj_in.qas
            ])
        if obj_in.devs:
            project_users.extend([
                ProjectUser(project_id=db_obj.id, user_id=user.id, role=ProjectRole.DEV)
                for user in obj_in.devs
            ])

        db.add_all(project_users)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Project, obj_in: ProjectUpdate
    ) -> Project:
        await super().update(
            db,
            db_obj=db_obj,
            obj_in=obj_in.model_dump(
                exclude_unset=True,
                exclude={"owners", "qas", "devs"}
            )
        )

        # 删除旧的关联
        await db.execute(
            delete(ProjectUser).where(ProjectUser.project_id == db_obj.id)
        )

        if obj_in.owners:
            db.add_all([
                ProjectUser(project_id=db_obj.id, user_id=user.id, role=ProjectRole.OWNER)
                for user in obj_in.owners
            ])

        if obj_in.qas:
            db.add_all([
                ProjectUser(project_id=db_obj.id, user_id=user.id, role=ProjectRole.QA)
                for user in obj_in.qas
            ])

        if obj_in.devs:
            db.add_all([
                ProjectUser(project_id=db_obj.id, user_id=user.id, role=ProjectRole.DEV)
                for user in obj_in.devs
            ])

        await db.commit()
        await db.refresh(db_obj)

        return db_obj


project = CRUDProject(Project)
