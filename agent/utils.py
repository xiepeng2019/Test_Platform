import asyncio
import os
import socket
import aiohttp
import json
import consul
import docker
import docker.errors

from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Union, Coroutine, Any, Dict
from loguru import logger
from fastapi import WebSocket
from const import (
    CONTAINER_STOP_HOOKS,
    GITLAB_ACCESS_TOKEN,
    LOG_HOST_DIR,
    SERVER_IP,
    TASK_SETTINGS_MAP,
)

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

async def stream_full_log_file(log_path: str, websocket: WebSocket):
    """WebSocket 日志实时推送"""
    # 检查文件行数，如果超过500行则只读取最后500行
    max_lines = 500
    with open(log_path, "r") as f:
        lines = f.readlines()

    if len(lines) > max_lines:
        # 发送最近500行历史日志
        for line in lines[-max_lines:]:
            await websocket.send_text(line.strip())
        # 记录当前文件读取位置
        position = len(''.join(lines))
    else:
        # 发送所有历史日志
        for line in lines:
            await websocket.send_text(line.strip())
        position = len(''.join(lines))

    # 实时监听日志文件新增内容
    with open(log_path, "r") as f:
        # 跳到上次读取的位置
        f.seek(position)
        while True:
            line = f.readline()
            if not line:
                await asyncio.sleep(0.2)
                continue
            await websocket.send_text(line.strip())


def get_plugin_path():
    """返回测试运行插件的路径（用于容器内挂载）"""
    return Path(__file__).parent / 'test_runner_plugin'


class Local:
    """本地主机信息类"""
    ip = None

    @staticmethod
    def get_local_ip():
        """获取本地主机IP地址"""
        if Local.ip:
            return Local.ip
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 创建UDP套接字
        try:
            s.connect(('10.255.255.255', 1))  # 连接到广播地址，端口1（UDP协议）
            Local.ip = s.getsockname()[0]  # 获取本地套接字绑定的IP地址（即主机IP）
        except Exception:
            Local.ip = '127.0.0.1'
        finally:
            s.close()
        return Local.ip


class DockerContainerHandler:
    """Docker 容器操作处理类"""
    def __init__(self, job_id: str):
        self.job_id = job_id  # 任务ID
        self.container_name = f"task-{job_id}"  # 容器名（与任务ID绑定）
        self.log_dir = LOG_HOST_DIR / f'job_{job_id}' # 任务日志目录（本地路径，将挂载到容器内）
        self.log_dir.mkdir(parents=True, exist_ok=True, mode=0o777)  # 创建目录（权限777）
        self.plugin_path = Path(__file__).parent / 'test_runner_plugin'  # 测试插件路径
        self.pip_cache_path = Path(__file__).parent / '.cache' / 'pip'  # pip缓存路径（加速依赖安装）
        self.pip_cache_path.mkdir(parents=True, exist_ok=True, mode=0o777)  # 创建目录（权限777）
        self.pytest_log_path = "/logs/pytest.log"  # 容器内测试日志路径

    async def stop(self):
        """停止容器并清理任务记录"""
        # 同步调用Docker SDK的stop方法（通过asyncio.to_thread适配同步函数）
        await asyncio.to_thread(self.container.stop)
        # 触发容器停止钩子（如向平台发送通知）
        await trigger_container_stop_hooks(self.job_id, TASK_SETTINGS_MAP[self.job_id])
        # 从全局任务字典中删除该任务
        if self.job_id in TASK_SETTINGS_MAP:
            del TASK_SETTINGS_MAP[self.job_id]
        return {"job_id": self.job_id, "status": "stopped"}

    @property
    def container(self):
        """获取当前任务对应的Docker容器实例"""
        return client.containers.get(self.container_name)

    @property
    async def logs(self):
        """获取容器日志(返回Docker原生日志)"""
        return self.container.logs()

    @property
    def env_vars(self):
        """获取任务的环境变量（从全局任务字典中提取）"""
        task_info = TASK_SETTINGS_MAP[self.job_id]
        if not task_info['env_vars']:
            return {}
        return {item['name']: item['value'] for item in task_info['env_vars']}

    async def delete(self):
        """强制删除容器并清理任务记录"""
        await asyncio.to_thread(self.container.remove, force=True)  # 强制删除（即使容器运行中）
        if self.job_id in TASK_SETTINGS_MAP:
            del TASK_SETTINGS_MAP[self.job_id]

    async def get_task_cmd(self):
        """生成容器内执行测试的Shell命令"""
        task_info = TASK_SETTINGS_MAP[self.job_id]
        # 构建Shell命令（分步骤执行：拉代码→装依赖→执行测试→归档日志）
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
        """处理Git仓库地址(添加GitLab令牌, 避免权限问题)"""
        task_info = TASK_SETTINGS_MAP[self.job_id]
        if task_info['repo'].startswith("https://"):
            repo_url = task_info['repo'].replace(
                "https://", f"https://oauth2:{GITLAB_ACCESS_TOKEN}@")
        else:
            repo_url = task_info['repo']
        return repo_url

    @property
    def cases_index(self):
        """获取测试用例索引（转为空格分隔的字符串）"""
        task_info = TASK_SETTINGS_MAP[self.job_id]
        return ' '.join(task_info['test_case_index'])

    @property
    def task_image(self):
        """获取任务使用的Docker镜像（从全局任务字典中提取）"""
        task_info = TASK_SETTINGS_MAP[self.job_id]
        return task_info['image']

    def _get_task_env_vars(self):
        """构建容器内的环境变量（包含系统级配置）"""
        task_info = TASK_SETTINGS_MAP[self.job_id]
        # 合并任务环境变量与服务器配置
        if task_info['server']:
            config = {**self.env_vars, **task_info['server']}
        else:
            config = self.env_vars
        # 返回容器内需要的环境变量
        return {
            "PYTHONPATH": '/plugins:/app',  # Python路径（包含插件和测试代码）
            "PYTHONUNBUFFERED": "1",  # 关闭Python输出缓冲（实时打印日志）
            "SERVER_IP": SERVER_IP or '',  # 服务器IP
            "TASK_ID": str(task_info["id"]),  # 任务ID
            "WALLY_CONFIG": json.dumps(config),  # 其他配置（JSON字符串）
        }

    def _get_task_volume(self):
        """构建容器挂载卷（本地路径与容器路径映射）"""
        return {
            str(self.pip_cache_path): {'bind': '/root/.cache/pip', 'mode': 'rw'},  # pip缓存（读写）
            str(self.plugin_path): {'bind': '/plugins', 'mode': 'ro'},  # 测试插件（只读）
            str(self.log_dir): {'bind': '/logs', 'mode': 'rw'},  # 日志目录（读写）
        }

    async def execute_docker_task(self):
        """创建并运行Docker容器，执行测试任务"""
        command = await self.get_task_cmd()
        logger.debug(f"执行命令: {command}")
        logger.debug(f"环境变量: {self.env_vars}")

        # 启动Docker容器（detach=True：后台运行）
        container = client.containers.run(
            self.task_image,  # 容器镜像（如python:3.10）
            command=f'sh -c "{command}"',  # 执行Shell命令
            name=self.container_name,  # 容器名
            detach=True,  # 后台运行
            auto_remove=False,  # 不自动删除（需手动清理）
            volumes=self._get_task_volume(),  # 挂载卷配置
            environment=self._get_task_env_vars(),  # 环境变量配置
        )

        result = await asyncio.to_thread(container.wait) # 等待容器执行完成（获取退出状态）
        TASK_SETTINGS_MAP[self.job_id]["container_id"] = container.id # 更新全局任务字典中的容器ID和状态
        if result["StatusCode"] == 0:  # 退出码0表示成功
            TASK_SETTINGS_MAP[self.job_id]["status"] = "succeeded"
        else:  # 非0退出码表示失败
            TASK_SETTINGS_MAP[self.job_id]["status"] = "failed"

    async def run(self):
        """启动测试任务（入口方法）"""
        try:
            await self.execute_docker_task()
        except docker.errors.ContainerError as e:
            TASK_SETTINGS_MAP[self.job_id]["status"] = "failed" # 容器执行出错（如命令错误）
        except Exception as e:
            logger.exception(e)
            TASK_SETTINGS_MAP[self.job_id]["status"] = "failed"
        finally:
            # 无论成功失败，都触发容器停止钩子
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
    """清理创建时间超过一天且状态为退出的容器"""
    logger.info("开始执行过期容器清理任务")
    try:
        one_day_ago = datetime.now() - timedelta(days=1)
        # 获取所有容器（包括已停止状态）
        containers = await asyncio.to_thread(client.containers.list, all=True)

        for container in containers:
            # 解析容器创建时间
            create_time_str = container.attrs["Created"].split(".")[0]
            create_time = datetime.strptime(create_time_str, "%Y-%m-%dT%H:%M:%S")

            # 检查是否满足清理条件
            if create_time < one_day_ago and container.status == "exited":
                logger.info(f"清理过期容器：{container.name} (ID: {container.id[:12]})")
                try:
                    # 停止并删除容器
                    await asyncio.to_thread(container.stop)
                    await asyncio.to_thread(container.remove)
                    logger.success(f"容器 {container.name} 清理完成")

                    # 同步删除内存中的任务记录
                    job_id = container.name.replace("task-", "")
                    if job_id in TASK_SETTINGS_MAP:
                        del TASK_SETTINGS_MAP[job_id]
                        logger.info(f"同步删除任务记录：{job_id}")

                except docker.errors.APIError as e:
                    logger.error(f"清理容器 {container.name} 失败：{str(e)}")
                except docker.errors.APIError as e:
                    logger.error(f"清理容器 {container.name} 失败：{str(e)}")

    except Exception as e:
        logger.error(f"容器清理任务执行失败：{str(e)}")
    logger.info("过期容器清理任务执行完毕")


async def sync_task_and_container_status():
    """同步数据库任务状态和容器实际状态"""
    logger.info("开始同步任务状态与容器状态")
    try:
        # 获取所有容器并构建名称映射
        containers = await asyncio.to_thread(client.containers.list, all=True)
        container_map: Dict[str, Any] = {container.name: container for container in containers}

        # 检查所有任务状态
        for job_id, task_info in list(TASK_SETTINGS_MAP.items()):
            container_name = f"task-{job_id}"
            container = container_map.get(container_name)

            # 任务存在但容器已消失的情况
            if not container:
                if task_info["status"] not in ["succeeded", "failed", "stopped"]:
                    logger.warning(f"任务 {job_id} 的容器已消失, 更新状态为failed")
                    task_info["status"] = "failed"
                    await trigger_container_stop_hooks(job_id, task_info)
                continue

            # 根据容器状态更新任务状态
            if container.status == "exited":
                if task_info["status"] not in ["succeeded", "failed", "stopped"]:
                    exit_code = container.attrs["State"]["ExitCode"]
                    new_status = "succeeded" if exit_code == 0 else "failed"
                    logger.info(f"容器 {container_name} 已退出，更新任务状态为 {new_status}")
                    task_info["status"] = new_status
                    await trigger_container_stop_hooks(job_id, task_info)
            elif container.status == "running":
                if task_info["status"] != "running":
                    logger.info(f"容器 {container_name} 正在运行, 更新任务状态为running")
                    task_info["status"] = "running"
            elif container.status in ["paused", "restarting"]:
                if task_info["status"] != container.status:
                    logger.info(f"容器 {container_name} 状态为 {container.status}，更新任务状态")
                    task_info["status"] = container.status

    except Exception as e:
        logger.error(f"同步任务状态失败: {str(e)}")
    logger.info("任务状态与容器状态同步完成")


async def periodic_task():
    """定时任务主函数, 每60秒执行一次"""
    while True:
        try:
            # 执行容器清理
            await clean_expired_containers()
            # 执行状态同步
            await sync_task_and_container_status()
        except Exception as e:
            logger.error(f"定时任务执行出错: {str(e)}")

        # 等待60秒后再次执行
        await asyncio.sleep(60)


def start_periodic_tasks():
    """启动定时任务"""
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_task())
    logger.info("定时任务已启动, 将每60秒执行一次")


# 注册默认hook
register_container_stop_hook(default_container_stop_hook)
register_agent_service()
# 启动定时任务
start_periodic_tasks()

if __name__ == "__main__":
    print(get_plugin_path())

    # 用于本地测试
    # import uvicorn
    # from fastapi import FastAPI
    #
    # app = FastAPI()
    # uvicorn.run(app, host="0.0.0.0", port=8001)
