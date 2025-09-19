# MiniCPM-V服务器部署指南

## 快速开始

### 1. 一键部署

```bash
# 运行自动部署脚本
./deploy.sh
```

脚本会自动：
- 检查系统依赖（Docker、NVIDIA Docker）
- 验证模型文件
- 选择部署模式
- 构建并启动服务
- 执行健康检查

### 2. 手动部署

#### 开发环境

```bash
# 构建并启动
docker compose -f docker/docker-compose.yml up -d --build

# 检查状态
docker compose -f docker/docker-compose.yml ps

# 查看日志
docker compose -f docker/docker-compose.yml logs -f
```

#### 生产环境

```bash
# 启动生产服务
docker compose -f docker/docker-compose.prod.yml up -d --build

# 启动生产服务 + Nginx反向代理
docker compose -f docker/docker-compose.prod.yml --profile with-nginx up -d --build
```

## 部署要求

### 系统要求

- **操作系统**: Linux (推荐 Ubuntu 20.04+)
- **内存**: 最少 16GB RAM
- **GPU**: NVIDIA GPU (推荐 8GB+ VRAM)
- **存储**: 20GB+ 可用空间

### 软件依赖

- Docker 20.10+
- Docker Compose 2.0+
- NVIDIA Docker Runtime (GPU支持)

### 安装NVIDIA Docker

```bash
# 添加NVIDIA Docker仓库
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
   && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
   && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# 安装nvidia-docker2
sudo apt-get update && sudo apt-get install -y nvidia-docker2

# 重启Docker
sudo systemctl restart docker
```

## 部署配置

### 环境变量

创建 `.env` 文件配置：

```bash
# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8207
HOST_PORT=8207

# 模型配置
MODEL_PATH=./models

# 日志级别
LOG_LEVEL=INFO
```

### 端口配置

- **8207**: API服务端口
- **80**: Nginx HTTP端口（可选）
- **443**: Nginx HTTPS端口（可选）

## 服务管理

### 基本操作

```bash
# 查看服务状态
docker compose -f docker/docker-compose.yml ps

# 启动服务
docker compose -f docker/docker-compose.yml up -d

# 停止服务
docker compose -f docker/docker-compose.yml down

# 重启服务
docker compose -f docker/docker-compose.yml restart

# 查看日志
docker compose -f docker/docker-compose.yml logs -f
```

### 模型管理

```bash
# 加载模型
curl -X POST "http://localhost:8207/load-model" \
  -H "Content-Type: application/json" \
  -d '{"model_name": "MiniCPM-V-4_5-int4"}'

# 卸载模型
curl -X POST "http://localhost:8207/unload-model"

# 查看模型状态
curl "http://localhost:8207/models"
```

## 监控和维护

### 健康检查

```bash
# 检查服务健康状态
curl http://localhost:8207/health

# 响应示例
{
  "status": "healthy",
  "service": "MiniCPM-V Server",
  "version": "0.1.0"
}
```

### 日志管理

```bash
# 查看实时日志
docker compose logs -f minicpm-v-server

# 查看特定时间段日志
docker compose logs --since="2h" minicpm-v-server

# 导出日志
docker compose logs --no-color minicpm-v-server > server.log
```

### 性能监控

```bash
# 监控容器资源使用
docker stats minicpm-v-server

# 监控GPU使用
nvidia-smi -l 1
```

## 故障排除

### 常见问题

1. **GPU不可用**
   ```bash
   # 检查NVIDIA驱动
   nvidia-smi
   
   # 检查Docker GPU支持
   docker run --rm --gpus all nvidia/cuda:12.1-base nvidia-smi
   ```

2. **内存不足**
   ```bash
   # 调整模型量化级别
   # 使用更小的模型
   # 增加系统内存
   ```

3. **端口冲突**
   ```bash
   # 修改.env文件中的HOST_PORT
   HOST_PORT=8208
   ```

4. **模型加载失败**
   ```bash
   # 检查模型文件完整性
   ls -la models/
   
   # 检查权限
   chmod -R 755 models/
   ```

### 日志分析

```bash
# 查看错误日志
docker compose logs minicpm-v-server | grep ERROR

# 查看模型加载日志
docker compose logs minicpm-v-server | grep "Loading model"

# 查看API请求日志
docker compose logs minicpm-v-server | grep "POST\\|GET"
```

## 扩展部署

### 负载均衡

可以部署多个服务实例并使用Nginx负载均衡：

```yaml
# docker-compose.scale.yml
services:
  minicpm-v-server-1:
    extends:
      file: docker-compose.prod.yml
      service: minicpm-v-server
    container_name: minicpm-v-server-1
    environment:
      - CUDA_VISIBLE_DEVICES=0

  minicpm-v-server-2:
    extends:
      file: docker-compose.prod.yml
      service: minicpm-v-server
    container_name: minicpm-v-server-2
    environment:
      - CUDA_VISIBLE_DEVICES=1
```

### SSL配置

1. 将SSL证书放在 `docker/ssl/` 目录
2. 取消注释 `nginx.conf` 中的HTTPS配置
3. 重启Nginx服务

## API使用示例

### 图片分析

```bash
# 上传图片分析
curl -X POST "http://localhost:8207/analyze" \
  -F "file=@image.jpg" \
  -F "prompt=请描述这张图片"

# URL图片分析
curl -X POST "http://localhost:8207/analyze-url" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "prompt": "请描述这张图片的内容"
  }'
```

### API文档

部署完成后访问：
- Swagger UI: http://localhost:8207/docs
- ReDoc: http://localhost:8207/redoc