# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此仓库中工作提供指导。

## 项目概述

这是一个基于 FastAPI 的服务器，用于提供基于 MiniCPM-V 视觉模型的图片分析服务。项目目标：
- 提供基于 MiniCPM-V 模型的图片分析功能
- 通过 HTTP API 接口支持图片 URL 或文件上传进行分析
- 构建稳定可靠的图片分析服务

## 架构

**核心结构：**
- `src/main.py` - FastAPI 应用入口点，包含基础健康检查和模型列表接口
- `models/` - 包含已下载的模型文件（MiniCPM-V-4_5-int4 和 MiniCPM-V-4-int4）
- `docker/` - 容器化配置，包含 Dockerfile 和 docker-compose.yml
- 当前状态：基础 FastAPI 脚手架，尚未实现推理功能

**关键设计：**
- 模型目录在容器中以只读方式挂载到 `/app/models`
- 基于环境变量的配置（主机、端口、模型路径）
- 为逐步添加推理依赖做好准备（torch、transformers 等）

## 开发命令

**本地开发：**
```bash
# 安装依赖
pip install -r REQUIREMENTS.TXT

# 本地运行服务器
PYTHONPATH=src python -m uvicorn main:app --host 0.0.0.0 --port 8207

# 健康检查
curl -f http://127.0.0.1:8207/health

# 查看可用模型
curl -s http://127.0.0.1:8207/models | jq .
```

**Docker 开发：**
```bash
# 构建并启动
docker compose -f docker/docker-compose.yml up -d --build

# 检查状态
docker compose -f docker/docker-compose.yml ps

# 查看日志
docker compose -f docker/docker-compose.yml logs -f

# 健康检查
curl -f http://localhost:8207/health

# 停止并清理
docker compose -f docker/docker-compose.yml down

# 从零重新构建
docker compose -f docker/docker-compose.yml build --no-cache
```

## 模型信息

**可用模型：**
- `MiniCPM-V-4_5-int4/` - 最新版本，使用 int4 量化
- `MiniCPM-V-4-int4/` - 之前版本，使用 int4 量化

两个模型都包含完整的模型文件、分词器和配置，已准备好进行推理实现。

## 下一步实现

当前代码库是最小化脚手架。要添加推理功能：

1. **添加依赖：** 逐步在 REQUIREMENTS.TXT 中引入 torch、transformers、safetensors、accelerate
2. **实现模型加载：** 创建模型管理服务来加载和缓存模型
3. **添加推理接口：** 
   - POST `/analyze` 用于文件上传
   - POST `/analyze-url` 用于图片 URL
4. **缓存管理：** 配置 HF_HOME/TRANSFORMERS_CACHE 用于模型缓存

## 环境变量

- `SERVER_HOST` (默认: 0.0.0.0)
- `SERVER_PORT` (默认: 8207) 
- `MODEL_PATH` (默认: ./models, 容器内: /app/models)

## 重要说明

- 模型目录在容器中以只读方式挂载
- 本地开发使用 PYTHONPATH=src
- 当前脚手架已移除所有推理依赖 - 需要逐步添加
- 专注于真实数据测试（按项目要求不使用模拟/虚假数据）