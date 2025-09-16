from app.crud.base import CRUDBase
from app.models import Bug
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.bug.bug import BugCases
from app.schemas.bug.bug import (BugCreate, BugUpdate)


class CRUDBug(CRUDBase[Bug, BugCreate, BugUpdate]):

    async def create_bug(self, db: AsyncSession, obj_in: BugCreate, project_id: int) -> Bug:
        """Create new data """
        bug_obj = Bug(**{
            **obj_in.model_dump(exclude={"test_case_id"}),
            'project_id': project_id
        })
        db.add(bug_obj)
        await db.flush()

        if obj_in.test_case_id:
            case_links = [
                BugCases(**{
                    "bug_id": bug_obj.id,
                    "testcase_id": case_index,
                })
                for case_index in obj_in.test_case_id
            ]
            db.add_all(case_links)

        await db.commit()
        await db.refresh(bug_obj)
        return bug_obj


bug = CRUDBug(Bug)
