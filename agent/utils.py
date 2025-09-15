import asyncio
from typing import Dict, Any
import os
import socket
import aiohttp
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Union, Coroutine, Any

from loguru import logger
from fastapi import WebSocket
import consul
import docker
import docker.errors

from const import (
    CONTAINER_STOP_HOOKS,
    GITLAB_ACCESS_TOKEN,
    LOG_HOST_DIR,
    PIP_CACHE_DIR,
    SERVER_IP,
    TASK_SETTINGS_MAP,
)

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

async def stream_full_log_file(log_path: str, websocket: WebSocket):
    # 检查文件行数，如果超过500行则只读取最后500行
    max_lines = 500
    with open(log_path, "r") as f:
        lines = f.readlines()

    if len(lines) > max_lines:
        # 只发送最后max_lines行
        for line in lines[-max_lines:]:
            await websocket.send_text(line.strip())
        position = len(''.join(lines))
    else:
        # 发送所有历史日志
        for line in lines:
            await websocket.send_text(line.strip())
        position = len(''.join(lines))

    with open(log_path, "r") as f:
        f.seek(position)
        while True:
            line = f.readline()
            if not line:
                await asyncio.sleep(0.2)
                continue
            await websocket.send_text(line.strip())


def get_plugin_path():
    """获取插件路径"""
    return Path(__file__).parent / 'test_runner_plugin'


class Local:
    ip = None

    @staticmethod
    def get_local_ip():
        if Local.ip:
            return Local.ip
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            Local.ip = s.getsockname()[0]
        except Exception:
            Local.ip = '127.0.0.1'
        finally:
            s.close()
        return Local.ip


class DockerContainerHandler:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.container_name = f"task-{job_id}"
        self.log_dir = LOG_HOST_DIR / f'job_{job_id}'
        self.log_dir.mkdir(parents=True, exist_ok=True, mode=0o777)
        self.plugin_path = Path(__file__).parent / 'test_runner_plugin'
        self.pip_cache_path = Path(__file__).parent / '.cache' / 'pip'
        self.pip_cache_path.mkdir(parents=True, exist_ok=True, mode=0o777)
        self.pytest_log_path = "/logs/pytest.log"

    async def stop(self):
        await asyncio.to_thread(self.container.stop)
        await asyncio.to_thread(trigger_container_stop_hooks, self.job_id, TASK_SETTINGS_MAP[self.job_id])
        if self.job_id in TASK_SETTINGS_MAP:
            del TASK_SETTINGS_MAP[self.job_id]
        return {"job_id": self.job_id, "status": "stopped"}

    @property
    def container(self):
        return client.containers.get(self.container_name)

    @property
    async def logs(self):
        return self.container.logs()

    @property
    def env_vars(self):
        task_info = TASK_SETTINGS_MAP[self.job_id]
        if not task_info['env_vars']:
            return {}
        return {item['name']: item['value'] for item in task_info['env_vars']}

    async def delete(self):
        await asyncio.to_thread(self.container.remove, force=True)
        if self.job_id in TASK_SETTINGS_MAP:
            del TASK_SETTINGS_MAP[self.job_id]

    async def get_task_cmd(self):
        task_info = TASK_SETTINGS_MAP[self.job_id]
        command = f"""\
            ( \
            echo '🐳 Git clone test repo' && \
            git clone --depth=1 -b {task_info['branch']} {self.git_repo} /app && \
            echo '🐳 Install requirements' && \
            pip install -r /app/requirements.txt && \
            pip install requests && \
            pip install loguru && \
            echo '🐳 Run pytest' && \
            echo '🐳 Case indices: {self.cases_index}' && \
            echo '🐳 Env vars: {self.env_vars}' && \
            python /plugins/find_test_cases.py {self.cases_index} --project-root /app/test_case --run \
            ) 2>&1 | tee -a {self.pytest_log_path} && \
            tar -czvf /logs/log.tar.gz /app/TestLog
        """
        return command

    @property
    def git_repo(self):
        task_info = TASK_SETTINGS_MAP[self.job_id]
        if task_info['repo'].startswith("https://"):
            repo_url = task_info['repo'].replace(
                "https://", f"https://oauth2:{GITLAB_ACCESS_TOKEN}@")
        else:
            repo_url = task_info['repo']
        return repo_url

    @property
    def cases_index(self):
        task_info = TASK_SETTINGS_MAP[self.job_id]
        return ' '.join(task_info['test_case_index'])

    @property
    def task_image(self):
        task_info = TASK_SETTINGS_MAP[self.job_id]
        return task_info['image']

    def _get_task_env_vars(self):
        task_info = TASK_SETTINGS_MAP[self.job_id]
        if task_info['server']:
            config = {**self.env_vars, **task_info['server']}
        else:
            config = self.env_vars

        return {
            "PYTHONPATH": '/plugins:/app',
            "PYTHONUNBUFFERED": "1",
            "SERVER_IP": SERVER_IP or '',
            "TASK_ID": str(task_info["id"]),
            "WALLY_CONFIG": json.dumps(config),
        }

    def _get_task_volume(self):
        return {
            str(self.pip_cache_path): {'bind': '/root/.cache/pip', 'mode': 'rw'},
            str(self.plugin_path): {'bind': '/plugins', 'mode': 'ro'},
            str(self.log_dir): {'bind': '/logs', 'mode': 'rw'},
        }

    async def execute_docker_task(self):
        command = await self.get_task_cmd()
        logger.debug(command)
        logger.debug(self.env_vars)
        container = client.containers.run(
            self.task_image,
            command=f'sh -c "{command}"',
            name=self.container_name,
            detach=True,
            auto_remove=False,
            volumes=self._get_task_volume(),
            environment=self._get_task_env_vars(),
        )

        result = await asyncio.to_thread(container.wait)
        TASK_SETTINGS_MAP[self.job_id]["container_id"] = container.id
        if result["StatusCode"] == 0:
            TASK_SETTINGS_MAP[self.job_id]["status"] = "succeeded"
        else:
            TASK_SETTINGS_MAP[self.job_id]["status"] = "failed"

    async def run(self):
        try:
            await self.execute_docker_task()
        except docker.errors.ContainerError as e:
            TASK_SETTINGS_MAP[self.job_id]["status"] = "failed"
        except Exception as e:
            logger.exception(e)
            TASK_SETTINGS_MAP[self.job_id]["status"] = "failed"
        finally:
            # 容器异常停止后也触发hooks
            await trigger_container_stop_hooks(self.job_id, TASK_SETTINGS_MAP[self.job_id])


def register_agent_service():
    try:
        host = os.getenv("CONSUL_SERVER")
        local_ip = Local.get_local_ip()
        if not host:
            logger.error("Consul server host not set")
            raise Exception("Consul server host not set")
        c = consul.Consul(host=host, port=8500)
        c.agent.service.register(
            name=os.getenv("AGENT_NAME"),
            service_id=f"agent-{local_ip}",
            address=local_ip,
            port=9001,
            tags=["agent"],
            check=consul.Check().http(
                f"http://{local_ip}:9001/heartbeat", interval="10s", timeout="2s", deregister="2s")
        )
    except Exception as e:
        logger.error(f"Register consul service failed, error: {e}")


def register_container_stop_hook(hook: Callable[[str, Dict[str, Any]], Union[None, Coroutine[Any, Any, None]]]):
    """注册容器停止后的hook函数"""
    CONTAINER_STOP_HOOKS.append(hook)


async def default_container_stop_hook(job_id: str, task_info: Dict[str, Any]):
    """默认的容器停止hook, 向平台发送通知"""
    server_ip = os.getenv('SERVER_IP')
    if not server_ip:
        logger.warning(
            "SERVER_IP not set, skipping container stop notification")
        return
    platform_url = f"{server_ip}/api/test_task/record/{job_id}/container_stop"
    payload = {
        "status": task_info.get("status", "unknown").capitalize(),
        "container_id": task_info.get("container_id"),
        "timestamp": datetime.now().isoformat()
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(platform_url, json=payload) as response:
                if response.status == 200:
                    logger.info(
                        f"Successfully notified platform about container stop for job {job_id}")
                else:
                    logger.error(f"Failed to notify platform: {response.status}")
                    logger.error(f"Response content: {await response.text()}")
    except Exception as e:
        logger.error(f"Error notifying platform about container stop: {e}")


async def trigger_container_stop_hooks(job_id: str, task_info: Dict[str, Any]):
    """触发所有注册的容器停止hooks"""
    logger.info(f"Triggering {len(CONTAINER_STOP_HOOKS)} container stop hooks for job {job_id}")
    for hook in CONTAINER_STOP_HOOKS:
        try:
            if asyncio.iscoroutinefunction(hook):
                await hook(job_id, task_info)
            else:
                hook(job_id, task_info)
        except Exception as e:
            logger.error(f"Error in container stop hook: {e}")

async def clean_expired_containers():
    """清理：创建时间超过24小时且状态为退出（exited）的容器"""
    logger.info("开始执行过期容器清理任务")
    # 1. 定义时间阈值（当前时间 - 24小时）
    one_day_ago = datetime.now() - timedelta(days=1)
    # 2. 遍历所有容器（包括停止的）
    try:
        containers = client.containers.list(all=True)  # all=True 显示所有容器（包括已停止）
        for container in containers:
            # 3. 解析容器创建时间（Docker 时间格式：2024-05-20T12:34:56.789012345Z）
            create_time_str = container.attrs["Created"].split(".")[0]  # 截取到秒级
            create_time = datetime.strptime(create_time_str, "%Y-%m-%dT%H:%M:%S")
            # 4. 筛选条件：创建时间超过24小时 + 状态为 exited
            if create_time < one_day_ago and container.status == "exited":
                logger.info(f"清理过期容器：{container.name}（ID: {container.id[:12]}），创建时间：{create_time}")
                # 5. 停止容器（若未完全停止）并删除
                try:
                    await asyncio.to_thread(container.stop)  # 确保容器停止
                    await asyncio.to_thread(container.remove)  # 删除容器
                    logger.success(f"容器 {container.name} 清理完成")
                except docker.errors.APIError as e:
                    logger.error(f"清理容器 {container.name} 失败：{str(e)}")
    except Exception as e:
        logger.error(f"容器清理任务执行失败：{str(e)}")
    logger.info("过期容器清理任务执行完毕")


# 注册默认hook
register_container_stop_hook(default_container_stop_hook)
register_agent_service()


if __name__ == "__main__":
    print(get_plugin_path())

    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8001)
