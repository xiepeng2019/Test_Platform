import asyncio
import os
import signal
import sys
import aiofiles

from fastapi.responses import StreamingResponse
from loguru import logger
from fastapi import FastAPI, HTTPException, WebSocket
import docker
import docker.errors

from const import (
    LOG_HOST_DIR,
    SERVER_IP,
    TASK_SETTINGS_MAP,
    TaskRunRequest,
)
from utils import (
    DockerContainerHandler,
    stream_full_log_file,
    trigger_container_stop_hooks,
)


app = FastAPI()

def signal_handler(signum, frame):
    logger.info("🛑 接收到关闭信号，正在优雅关闭服务...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
logger.info(f"SERVER_IP: {SERVER_IP}")
logger.info(f"LOG_HOST_DIR: {LOG_HOST_DIR}")


@app.post("/tasks/{job_id}/stop")
async def stop_task(job_id: str):
    try:
        container_handler = DockerContainerHandler(job_id)
        return await container_handler.stop()
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await trigger_container_stop_hooks(job_id, TASK_SETTINGS_MAP[job_id])


@app.get("/tasks/{job_id}")
async def get_task_status(job_id: str):
    if job_id not in TASK_SETTINGS_MAP:
        raise HTTPException(status_code=404, detail="Task not found")
    return TASK_SETTINGS_MAP[job_id]


@app.get("/tasks/{job_id}/log")
async def download_log(job_id: str):
    log_path = f"{LOG_HOST_DIR}/job_{job_id}/pytest.log"

    # 获取文件大小用于Content-Length头
    try:
        file_stat = await asyncio.to_thread(os.stat, log_path)
        file_size = file_stat.st_size
    except Exception as e:
        print(f"[Agent Error] Failed to get file size: {e}")
        file_size = None

    async def log_stream():
        try:
            async with aiofiles.open(log_path, mode='rb') as f:
                while True:
                    chunk = await f.read(1024)
                    if not chunk:
                        break
                    yield chunk
                    await asyncio.sleep(0)  # 让出事件循环，避免长时间占用
        except Exception as e:
            print(f"[Agent Error] Streaming failed: {e}")

    # 构建响应头
    headers = {}
    if file_size is not None:
        headers["Content-Length"] = str(file_size)

    return StreamingResponse(log_stream(), media_type="text/plain", headers=headers)


@app.get("/tasks", tags=['task'])
async def get_tasks():
    return TASK_SETTINGS_MAP


@app.get("/tasks/{job_id}/logs", tags=['task'])
async def get_task_logs(job_id: str):
    try:
        container_handler = DockerContainerHandler(job_id)
        return await container_handler.logs
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Task Container Not Found...")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Get container log failed: {e}')


@app.delete("/tasks/{job_id}", tags=['task'])
async def delete_task(job_id: str):
    try:
        container_handler = DockerContainerHandler(job_id)
        await container_handler.delete()
    except docker.errors.NotFound:
        return HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


@app.post("/run", tags=["task"])
async def execute_task(task_info: TaskRunRequest):
    tasks_key = str(task_info.job_id)
    if not task_info.cases_index:
        raise HTTPException(status_code=400, detail="Test case index is required")

    TASK_SETTINGS_MAP[tasks_key] = {
        "id": task_info.job_id,
        "repo": task_info.repo,
        "branch": task_info.branch,
        "test_case_index": task_info.cases_index,
        "image": task_info.image,
        "status": "created",
        "container_id": None,
        "env_vars": task_info.env_vars,
        "server": task_info.server,
    }
    container_handler = DockerContainerHandler(tasks_key)
    asyncio.create_task(container_handler.run())
    return TASK_SETTINGS_MAP[tasks_key]


@app.websocket("/ws/logs/{job_id}")
async def ws_logs(websocket: WebSocket, job_id: str):
    await websocket.accept()
    log_path = f"{LOG_HOST_DIR}/job_{job_id}/pytest.log"
    await stream_full_log_file(log_path, websocket)


@app.get("/heartbeat")
async def heartbeat():
    logger.debug(TASK_SETTINGS_MAP)
    return {"status": "alive"}
