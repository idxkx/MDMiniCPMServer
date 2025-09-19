# 项目结构说明

此文档描述了 MDMiniCPMServer 项目的文件组织结构。

## 目录结构

```
MDMiniCPMServer/
├── bin/                    # 执行脚本
│   ├── deploy.sh          # 部署脚本
│   ├── deploy.py          # Python部署脚本
│   └── start_server.py    # 服务器启动脚本
├── docs/                   # 文档目录
│   ├── API_GUIDE.md       # API使用指南
│   ├── CHANGES.md         # 变更日志
│   ├── DEPLOYMENT.md      # 部署文档
│   ├── AGENTS.md          # 代理配置文档
│   ├── SCAFFOLD.md        # 架构说明
│   ├── PROJECT_STRUCTURE.md # 项目结构说明
│   └── docker_build.log  # 构建日志
├── tests/                  # 测试文件
│   ├── *.py              # Python测试脚本
│   └── *.jpg             # 测试图片
├── src/                    # 源代码
│   ├── main.py           # FastAPI应用入口
│   └── model_service.py  # 模型服务管理
├── docker/                 # Docker相关配置
│   ├── Dockerfile        # 开发环境镜像
│   ├── Dockerfile.prod   # 生产环境镜像
│   ├── docker-compose.yml      # 开发环境编排
│   ├── docker-compose.prod.yml # 生产环境编排
│   ├── docker-compose.test.yml # 测试环境编排
│   └── nginx.conf        # Nginx配置
├── models/                 # 模型文件目录
│   ├── MiniCPM-V-4-int4/      # 模型4版本(符号链接)
│   └── MiniCPM-V-4_5-int4/    # 模型4.5版本(符号链接)
├── CLAUDE.md              # Claude工作指导
├── README.md              # 项目说明
├── REQUIREMENTS.TXT       # Python依赖
└── .env                   # 环境变量配置
```

## 文件分类原则

### bin/ - 可执行脚本
- 所有可执行的脚本文件
- 部署、启动、管理类脚本

### docs/ - 文档
- API文档、部署指南等说明文档
- 构建日志等记录文件
- 保留 `CLAUDE.md` 和 `README.md` 在根目录

### tests/ - 测试相关
- 单元测试、集成测试文件
- 测试用的图片、数据文件
- 调试脚本

### src/ - 源代码
- 应用的核心源代码
- 按模块组织的Python文件

## 模型文件说明

models/ 目录包含指向 HuggingFace 缓存的符号链接：
- `MiniCPM-V-4-int4` → `~/.cache/huggingface/hub/models--openbmb--MiniCPM-V-4-int4/snapshots/[hash]`
- `MiniCPM-V-4_5-int4` → `~/.cache/huggingface/hub/models--openbmb--MiniCPM-V-4_5-int4/snapshots/[hash]`

这种设计避免了重复存储模型文件，同时保持了项目结构的清晰性。

## 使用说明

### 部署
```bash
# 运行部署脚本
./bin/deploy.sh
```

### 开发测试
```bash
# 运行测试
python tests/test_model_load.py
```

### 查看文档
所有文档都在 `docs/` 目录下，根据需要查阅相应文档。