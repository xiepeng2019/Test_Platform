# 环境部署

## 开发
开发环境下，后端在容器中运行，前端在开发机上运行
其他组件使用 docker-compose 来管理容器。
```shell
docker-compose up -d
```

前端开发不使用docker容器中的前端代码，直接在开发机上起 dev
```bash
cd web
pnpm run dev
```

### 接口变更
后端接口变更需要严格声明类型, 标注 operation_id，并重新生成前端SDK
```bash
pnpm run openapi-ts
```

## 打包
生产环境打包流程和开发环境一致, 但是前端走docker file配置好的打包流程
```shell
docker-compose up --build
```

## DB
### 数据库迁移
#### 自动迁移
```shell
uv run alembic revision --autogenerate -m "update column"
uv run alembic upgrade head
```

#### 手动迁移
1. 生成脚本
```shell
uv run alembic revision --autogenerate -m "update column"
```
2. 手动修改 alembic/versions 目录下的迁移文件
```python
def upgrade():
    op.add_column('user', sa.Column('new_column', sa.String()))

def downgrade():
    op.drop_column('user', 'new_column')
```

3. 执行迁移
```shell
alembic upgrade head
```

## 配置
1. 修改前端配置 `web/public/config.js`

2. 修改后端配置 `.env`

`SECRET_KEY` 需要生成
```shell
openssl rand -hex 32
```

## 常见问题

### Docker 镜像拉不下来
参考链接: [解决 cn区域拉取docker hub 镜像超时问题](https://bytedance.larkoffice.com/docx/Yxrad5QCsobUFmxrTFHcxMNGn8i)

