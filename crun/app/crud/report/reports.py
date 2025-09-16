from app.crud.base import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.reports.report import TestReport
from app.schemas.reports.report import (TestReportsBase, TestReportCreate, TestReportUpdate)


class CRUDRepoet(CRUDBase[TestReport, TestReportCreate, TestReportUpdate]):

    async def create_report(self, db: AsyncSession, obj_in: TestReportCreate, project_id: int) -> TestReportsBase:
        """Create new data """
        report_obj = TestReportCreate(**{
            'project_id': project_id
        })
        db.add(report_obj)
        await db.flush()

        # if obj_in.test_case_id:
        #     case_links = [
        #         TestReportCreate(**{
        #             "bug_id": report_obj.id,
        #             "testcase_id": case_index,
        #         })
        #         for case_index in obj_in.test_case_id
        #     ]
        #     db.add_all(case_links)

        await db.commit()
        await db.refresh(report_obj)
        return report_obj


report = CRUDRepoet(TestReport)
