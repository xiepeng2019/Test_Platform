from app.crud.base import CRUDBase
from app.models import Bug
from app.schemas.bug.bug import BugCreate, BugUpdate


class CRUDBug(CRUDBase[Bug, BugCreate, BugUpdate]):
    ...


bug = CRUDBug(Bug)
