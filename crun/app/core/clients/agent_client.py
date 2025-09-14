import asyncio
from typing import List

import aiohttp
from fastapi.responses import StreamingResponse
from fastapi import HTTPException
from loguru import logger
import websockets

from app.config.config import get_settings


class AgentClient:
    def __init__(self, base_url: str):
        self.domain = base_url
        self.http_url = f'http://{base_url}:9001'
        self.ws_url = f'ws://{base_url}:9001'

    async def heartbeat(self) -> dict:
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(f'{self.http_url}/heartbeat', timeout=aiohttp.ClientTimeout(total=1, sock_connect=1)) as resp:
                    if resp.status != 200:
                        raise HTTPException(status_code=resp.status, detail=f'heartbeat failed, status: {resp.status}')
                    logger.info(f'heartbeat success, status: {resp.status}')
                    return await resp.json()
        except asyncio.CancelledError:
            logger.warning("Agent heartbeat cancelled")
            raise HTTPException(status_code=500, detail="Agent is not running")
        except asyncio.TimeoutError:
            logger.warning("Agent heartbeat timeout")
            raise HTTPException(status_code=500, detail="Agent is not running")
        except aiohttp.ClientError:
            logger.exception("Agent heartbeat failed")
            raise HTTPException(status_code=500, detail="Agent is not running")
        except Exception as e:
            logger.exception(f"Unexpected error during agent heartbeat: {e}")
            raise HTTPException(status_code=500, detail="Agent is not running")

    async def start_ws_to_agent(self, task_id: str, queue: asyncio.Queue):
        uri = f"{self.ws_url}/ws/logs/{task_id}"
        async with websockets.connect(uri) as ws:
            try:
                async for msg in ws:
                    await queue.put(msg)
            except Exception as e:
                await queue.put(f"[ERROR]: {e}")\

    async def run_task(
        self,
        job_id: int,
        repo: str,
        cases_index: List[str],
        image: str,
        branch: str,
        env_vars: List[dict] | None = None,
        server: dict | None = None,
    ) -> dict:
        async with aiohttp.ClientSession() as s:
            payload = {
                'job_id': job_id,
                'repo': repo,
                'cases_index': cases_index,
                'image': image,
                'branch': branch,
                'env_vars': env_vars,
                'server': server,
            }
            async with s.post(f'{self.http_url}/run', json=payload) as resp:
                if resp.status != 200:
                    logger.error(f'run task payload: {payload}')
                    logger.error(f'run task failed, status: {resp.status}')
                    logger.error(await resp.text())
                response = await resp.json()
                logger.debug(f'run task response: {response}')
                return response

    async def download_log(self, task_name: str, job_id: int) -> StreamingResponse:
        url = f"{self.http_url}/tasks/{job_id}/log"

        session_timeout = aiohttp.ClientTimeout(total=60)
        session = aiohttp.ClientSession(timeout=session_timeout)

        resp = await session.get(url)
        if resp.status != 200:
            text = await resp.text()
            await session.close()
            raise HTTPException(status_code=resp.status, detail=f"Agent error: {text}")

        # ✔ 直接返回 aiohttp 的原始 stream，包装成 StreamingResponse
        async def stream():
            try:
                async for chunk in resp.content.iter_any():
                    yield chunk
            except Exception as e:
                print(f"[Master Error] while streaming: {e}")
            finally:
                await resp.release()
                await session.close()

        return StreamingResponse(
            stream(),
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={task_name}_{job_id}.log",
                "Content-Length": resp.headers.get("Content-Length", "0")  # ✅ 添加Content-Length头
            }
        )



agent_client = AgentClient(get_settings().HOST_GATEWAY)
