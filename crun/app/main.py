import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.app:app", host="0.0.0.0", log_level="info") # 启动 FastAPI 应用实例