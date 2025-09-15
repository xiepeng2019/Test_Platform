import os
from typing import Dict, Any, List, Callable, Union, Coroutine
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
SERVER_IP = os.getenv("SERVER_IP")
GITLAB_ACCESS_TOKEN = os.getenv("GITLAB_ACCESS_TOKEN")
TASK_SETTINGS_MAP: Dict[str, Dict[str, Any]] = {}
CONTAINER_STOP_HOOKS: List[Callable[[str, Dict[str, Any]], Union[None, Coroutine[Any, Any, None]]]] = []
LOG_HOST_DIR = Path(__file__).parent / 'log' / 'test_logs'
LOG_HOST_DIR.mkdir(parents=True, exist_ok=True)
# PIP_PROXY = "https://bytedpypi.byted.org/simple"
PIP_CACHE_DIR = '/root/.cache/pip'

if not SERVER_IP:
    raise ValueError("SERVER_IP is not set")

if not GITLAB_ACCESS_TOKEN:
    raise ValueError("GITLAB_ACCESS_TOKEN is not set")


class TaskRunRequest(BaseModel):
    job_id: int
    repo: str = 'https://code.byted.org/hred/board_and_test_test.git'
    cases_index: List[str] = []
    image: str = "python:3.10"
    branch: str = 'dev_ada_laifu'
    env_vars: List[dict] | None = None
    server: dict | None = None
