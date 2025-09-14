# 安装部署

1. 安装 uv
```
curl -Ls https://astral.sh/uv/install.sh | sh

```

2. 启动 agent
```
nohup python3.10 -m uv run uvicorn main:app --port 9001 --reload > app.log 2>&1 &

```





1. 了解后端跟agent通信，以及怎么执行任务的
2. 怎么回传测试结果的？
3. 怎么实时显示日志？