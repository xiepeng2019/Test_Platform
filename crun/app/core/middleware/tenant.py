from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        project_id = request.headers.get('X-Project-Id')

        if not project_id:
            project_id = 0

        try:
            project_id = int(project_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid Project ID format"
            )

        # 将项目ID存入请求状态
        request.state.project_id = project_id

        response = await call_next(request)
        return response