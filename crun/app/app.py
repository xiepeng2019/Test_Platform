from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config.config import (get_settings)
from app.core.middleware.tenant import TenantMiddleware
from app.api.v1.routes import (
    user,
    project,
    auth,
    mock,
    test_plan,
)
from app.api.v1.routes.task import case_record, task_record, task, task_config
from app.api.v1.routes.case import cases, case_node
from app.api.v1.routes.resource import server
from app.api.v1.routes.bug.bug import bug_router
from app.api.v1.routes.report.report import report_router
from app.core.database import create_db_and_tables

settings = get_settings()

origins = [
    settings.FRONTEND_URL,
    settings.STATIC_URL
]

# 异步生命周期上下文管理器
# 用于管理 FastAPI 应用的启动和关闭过程，主要作用是在应用启动时执行初始化操作（如创建数据库表）。
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    # include_router用于路由模块化管理的核心方法，它允许将分散在不同文件中的子路由（APIRouter实例）整合到主应用或父路由中，实现代码的拆分与组织。
    app.include_router(user.router)
    app.include_router(auth.router, tags=["auth"])
    app.include_router(project.router, tags=["projects"])
    app.include_router(test_plan.router, tags=["plans"])
    app.include_router(cases.router, tags=["cases"])
    app.include_router(case_node.router, tags=["case-nodes"])
    app.include_router(task.router, tags=["tasks"])
    app.include_router(task_config.router, tags=["task-config"])
    app.include_router(task_record.router, tags=["task-record"])
    app.include_router(case_record.router, tags=["case-record"])
    app.include_router(server.router, tags=["resource"])
    app.include_router(mock.router, tags=["mock"])
    app.include_router(bug_router, tags=["bug"])
    app.include_router(report_router, tags=["report"])
    app.add_middleware(TenantMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )
    Instrumentator().instrument(app).expose(app)
    return app


app = create_app()
