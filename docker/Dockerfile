# 使用Python基础镜像，在运行时使用主机GPU
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 拷贝依赖文件并安装Python包
COPY REQUIREMENTS.TXT ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r REQUIREMENTS.TXT

# 拷贝源代码
COPY src/ ./src/

# 设置环境变量
ENV PYTHONPATH=/app/src \
    SERVER_HOST=0.0.0.0 \
    SERVER_PORT=8207 \
    CUDA_VISIBLE_DEVICES=0

EXPOSE 8207

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8207/health || exit 1

WORKDIR /app/src
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8207"]
