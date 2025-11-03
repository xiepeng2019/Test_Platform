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
        """
        心跳检测(验证Agent是否在线)
        :return: 包含心跳信息的字典
        """
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
        """
        建立 WebSocket 连接获取实时日志
        :param task_id: 任务ID
        :param queue: 用于存储日志消息的队列
        :return: None
        """
        uri = f"{self.ws_url}/ws/logs/{task_id}"
        async with websockets.connect(uri) as ws:
            try:
                async for msg in ws:
                    await queue.put(msg)
            except Exception as e:
                await queue.put(f"[ERROR]: {e}")\

    async def run_task(self, job_id: int,
                       repo: str,
                       cases_index: List[str],
                       image: str,
                       branch: str,
                       env_vars: List[dict] | None = None,
                       server: dict | None = None) -> dict:
        """
        触发任务执行
        :param job_id: 任务ID
        :param repo: 仓库URL
        :param cases_index: 测试用例索引列表
        :param image: 执行环境镜像
        :param branch: 分支名称
        :param env_vars: 环境变量列表
        :param server: 服务器配置
        :return: 包含任务执行信息的字典
        """
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
            # 发送 POST 请求到 Agent 的 /run 接口，触发任务执行
            async with s.post(f'{self.http_url}/run', json=payload) as resp:
                if resp.status != 200:
                    logger.error(f'run task payload: {payload}')
                    logger.error(f'run task failed, status: {resp.status}')
                    logger.error(await resp.text())
                response = await resp.json()
                logger.debug(f'run task response: {response}')
                return response

    async def download_log(self, task_name: str, job_id: int) -> StreamingResponse:
        """
        下载任务完整日志
        :param task_name: 任务名称
        :param job_id: 任务ID
        :return: 包含任务日志的 StreamingResponse
        """
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
            """
            流式返回任务日志
            :return: 任务日志的流式响应
            """
            try:
                async for chunk in resp.content.iter_any(): # 逐块读取日志内容
                    yield chunk # 流式返回给前端
            except Exception as e:
                print(f"[Master Error] while streaming: {e}")
            finally:
                await resp.release() # 释放响应资源
                await session.close() # 关闭会话

        return StreamingResponse(
            stream(),
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={task_name}_{job_id}.log",
                "Content-Length": resp.headers.get("Content-Length", "0")  # ✅ 添加Content-Length头
            }
        )



agent_client = AgentClient(get_settings().HOST_GATEWAY)
