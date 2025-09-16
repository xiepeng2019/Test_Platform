from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class TenantMiddleware(BaseHTTPMiddleware):
    # 中间件：异步函数，用于将请求传递给下一个处理环节，整体逻辑：暂停当前中间件的处理逻辑，将请求传递给下一个环节，
    # 下一个环节处理完成后并返回响应，拿到响应后在继续处理当前中间件的前后逻辑
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