# MiniCPM-V 视觉分析服务

基于 MiniCPM-V 模型的图片分析服务，支持通过 FastAPI 提供完整的视觉理解能力。

## 快速开始

### 一键部署（推荐）
```bash
./bin/deploy.sh
```

### 手动部署
```bash
# 本地开发
pip install -r REQUIREMENTS.TXT
cd src && python -m uvicorn main:app --host 0.0.0.0 --port 8207

# Docker部署
docker compose -f docker/docker-compose.yml up -d --build
```

### 验证部署
```bash
# 健康检查
curl -f http://localhost:8207/health

# 查看模型
curl -s http://localhost:8207/models

# API文档
http://localhost:8207/docs
```

## 项目结构
```
├── bin/          # 执行脚本 (deploy.sh, start_server.py)
├── src/          # 源代码 (main.py, model_service.py)  
├── tests/        # 测试文件和测试图片
├── docs/         # 文档目录
├── docker/       # Docker配置文件
├── models/       # 模型文件 (符号链接到HuggingFace缓存)
├── CLAUDE.md     # AI助手工作指导
└── README.md     # 项目说明
```

## 功能特性
- ✅ 支持 MiniCPM-V-4 和 MiniCPM-V-4.5 模型
- ✅ 图片文件上传分析
- ✅ 图片URL在线分析  
- ✅ 模型动态加载/卸载
- ✅ GPU/CPU自适应运行
- ✅ Docker容器化部署
- ✅ 完整的API文档

## 详细文档
- 项目结构: [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)
- API使用指南: [docs/API_GUIDE.md](docs/API_GUIDE.md)
- 部署说明: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

## 恢复推理功能（迁移建议）
1) 明确要支持的模型版本（先从体积小、依赖简单的版本开始）。
2) 渐进引入依赖：torch、transformers、safetensors、accelerate 等；在本地先验证再写入 Dockerfile。
3) 统一缓存/临时目录：将 HF_HOME/TRANSFORMERS_CACHE/TMPDIR 指向挂载卷（如 `/app/temp`）。
4) 处理动态模块：对含连字符的 `transformers_modules` 名称，使用别名目录或导入钩子；避免改写模型目录本身。
5) 健康与观测：为加载/推理路径加日志、超时与错误码；提供 `/model/load`、`/model/status` 等基础 API。
6) 持续集成：在 CI 中构建最小镜像并跑基本健康与加载用例，避免回归。
