# 脚手架说明（Fresh Server）

## 目标
- 提供最小可运行的 FastAPI + Docker Compose 脚手架；
- 保持 `models/` 为宿主机目录并以只读方式挂载至容器 `/app/models`；
- 便于后续逐步恢复/扩展推理能力。

## 目录结构
- src/: 应用源码（入口 `src/main.py`）
- docker/: Dockerfile 与 compose 文件
- models/: 模型目录（仅保留，容器内挂载到 `/app/models`）
- REQUIREMENTS.TXT, .env.example, README.md

## 本地运行
- 安装依赖：`pip install -r REQUIREMENTS.TXT`
- 启动：`PYTHONPATH=src python -m uvicorn main:app --host 0.0.0.0 --port 8207`
- 健康检查：`curl -f http://127.0.0.1:8207/health`
- 查看模型：`curl -s http://127.0.0.1:8207/models`

## Docker Compose
- 构建+启动：`docker compose -f docker/docker-compose.yml up -d --build`
- 查看状态：`docker compose -f docker/docker-compose.yml ps`
- 日志：`docker compose -f docker/docker-compose.yml logs -f`
- 健康检查：`curl -f http://localhost:8207/health`

## 环境变量（.env / .env.example）
- SERVER_HOST（默认 0.0.0.0）
- SERVER_PORT（默认 8207）
- MODEL_PATH（默认 `./models`，容器内固定为 `/app/models`）

## 模型目录
- 宿主机路径：`models/`；容器挂载：`/app/models`（只读）。
- 接口 `/models` 只做列表与粗略体积统计，不读取模型内容。

## 常用维护
- 停止/删除：`docker compose -f docker/docker-compose.yml down`
- 重新构建：`docker compose -f docker/docker-compose.yml build --no-cache`
- 清理 Docker 资源（慎用）：`docker system prune -af`

## 扩展建议
1. 在 `src/` 新增模块与路由（建议 `routers/`）并注册到 `main.py`；
2. 渐进式引入推理依赖（transformers/torch 等），优先在本地验证再进容器；
3. 将运行时缓存与临时目录统一到挂载卷（如 `/app/temp`）以避免容器层膨胀。

## 故障排查
- 端口占用：修改 `HOST_PORT` 或 `.env` 中的 `SERVER_PORT`；
- 模型不可见：确认 `models/` 存在并包含子目录，且已正确挂载；
- 构建失败：检查网络/源，或加 `--no-cache` 重新构建。
