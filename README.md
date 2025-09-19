# Fresh Server

最小可运行的 FastAPI + Docker Compose 脚手架，仅保留并挂载 `models/`。

## 本地运行
- Python: 3.10+
- 安装依赖: `pip install -r REQUIREMENTS.TXT`
- 启动: `PYTHONPATH=src python -m uvicorn main:app --host 0.0.0.0 --port 8207`

## Docker Compose
- 构建并启动: `docker compose -f docker/docker-compose.yml up -d --build`
- 健康检查: `curl -f http://localhost:8207/health`
- 查看模型: `curl -s http://localhost:8207/models | jq .`

## 目录
- src/: 应用源码（入口 `src/main.py`）
- models/: 模型目录（宿主机路径，Compose 只读挂载到 `/app/models`）
- docker/: Dockerfile 与 compose 文件

## 脚手架文档
- 详细说明见：docs/SCAFFOLD.md

## 恢复推理功能（迁移建议）
1) 明确要支持的模型版本（先从体积小、依赖简单的版本开始）。
2) 渐进引入依赖：torch、transformers、safetensors、accelerate 等；在本地先验证再写入 Dockerfile。
3) 统一缓存/临时目录：将 HF_HOME/TRANSFORMERS_CACHE/TMPDIR 指向挂载卷（如 `/app/temp`）。
4) 处理动态模块：对含连字符的 `transformers_modules` 名称，使用别名目录或导入钩子；避免改写模型目录本身。
5) 健康与观测：为加载/推理路径加日志、超时与错误码；提供 `/model/load`、`/model/status` 等基础 API。
6) 持续集成：在 CI 中构建最小镜像并跑基本健康与加载用例，避免回归。
