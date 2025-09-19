# NVIDIA Docker配置修复指南

## 问题描述
部署时出现警告：`NVIDIA Docker运行时未正确配置`

## 原因
Docker daemon缺少NVIDIA运行时配置

## 解决方案

### 1. 配置Docker daemon

创建或编辑 `/etc/docker/daemon.json`：

```bash
sudo nano /etc/docker/daemon.json
```

添加以下内容：

```json
{
    "default-runtime": "runc",
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
```

### 2. 重启Docker服务

```bash
sudo systemctl restart docker
```

### 3. 验证配置

```bash
# 检查运行时
docker info | grep -A 10 "Runtimes"

# 测试NVIDIA容器
docker run --rm --gpus all nvidia/cuda:12.1-base-ubuntu22.04 nvidia-smi
```

## 当前状态

虽然有警告，但Docker Compose配置使用了 `deploy.resources.reservations.devices` 方式，
仍然可以正常访问GPU：

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

## 验证GPU可用性

检查容器内GPU访问：

```bash
# 启动服务后检查
docker exec minicpm-v-server nvidia-smi

# 或查看容器日志中的设备信息
docker logs minicpm-v-server | grep -i cuda
```

## 临时解决方案

如果无法修改系统配置，服务仍然可以正常运行，
警告不会影响GPU功能。