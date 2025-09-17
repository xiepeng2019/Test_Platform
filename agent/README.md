# 安装部署

1. 安装 uv
```
curl -Ls https://astral.sh/uv/install.sh | sh

```

2. 启动 agent
```
nohup python3.10 -m uv run uvicorn main:app --port 9001 --reload > app.log 2>&1 &

```