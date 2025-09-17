import re
import inspect
import json
import os
import time
import pytest
import requests
from loguru import logger

case_start_time = {}
SERVER_IP = os.environ.get("SERVER_IP")
TASK_ID = os.environ.get("TASK_ID")
CONFIG = os.environ.get("WALLY_CONFIG", "{}")


def _send_test_result(item, report, start_time):
    """测试结果回调"""
    try:
        end_time = time.time()
        duration = end_time - start_time if start_time else report.duration
        result = {
            "record_id": TASK_ID,
            "result": {
                "case_node": report.nodeid,
                "result": report.outcome,
                "case_index": extract_case_id_from_function(item.function) or "",
                "start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)) or '',
                "end_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)),
                "duration": int(duration)
            }
        }
        response = requests.post(f'{SERVER_IP}/api/test_task/case_result', json=result)
        if response.status_code != 200:
            logger.error(f'❗上报结果出错, {item.nodeid}')
            logger.debug(json.dumps(result, indent=4))
            logger.debug(response.json())
        else:
            logger.info(f'✅ 上报结果成功, {response.json()}')
    except Exception as e:
        logger.error(f'❗上报结果出错, {item.nodeid}')
        logger.debug(e.with_traceback(Exception.__traceback__))


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """在 pytest 配置阶段创建 config.json 文件"""
    try:
        with open('/app/env.json', 'w', encoding='utf-8') as f:
            json.dump(json.loads(CONFIG), f, indent=4, ensure_ascii=False)

        logger.info(f"✅ 配置文件已创建: /app/env.json")
        with open('/app/env.json', 'r', encoding='utf-8') as f:
            config_content = json.load(f)
            logger.info(f"✅ 配置内容: {json.dumps(config_content, indent=4, ensure_ascii=False)}")
    except Exception as e:
        logger.error(f"❌ 创建配置文件失败: {str(e)}")


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_makereport(item, call):
    """ runtest hook"""
    if item.nodeid not in case_start_time:
        case_start_time[item.nodeid] = time.time()

    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        start_time = case_start_time.get(item.nodeid)
        _send_test_result(item, report, start_time)
    return outcome


def extract_case_id_from_function(func):
    """
    从函数 docstring 中提取 "测试编号: xxx"
    """
    doc = inspect.getdoc(func)
    if not doc:
        return None

    match = re.search(r"测试用例编号[:：]?\s*([^\s]+)", doc)
    if match:
        return match.group(1)
    return None

