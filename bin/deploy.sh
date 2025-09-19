#!/bin/bash

# MiniCPM-V服务器部署脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    # 检查NVIDIA Docker
    if command -v nvidia-smi &> /dev/null; then
        log_info "检测到NVIDIA GPU"
        if ! docker run --rm --gpus all nvidia/cuda:12.1-base-ubuntu22.04 nvidia-smi &> /dev/null; then
            log_warning "NVIDIA Docker运行时未正确配置"
            log_info "GPU仍可通过 Docker Compose 的 device 映射访问"
            log_info "如需完整配置，请参考: docs/NVIDIA_DOCKER_FIX.md"
        else
            log_success "NVIDIA Docker运行时配置正常"
        fi
    else
        log_warning "未检测到NVIDIA GPU，将使用CPU模式"
    fi
    
    log_success "依赖检查完成"
}

# 检查模型文件
check_models() {
    log_info "检查模型文件..."
    
    if [ ! -d "models" ]; then
        log_error "models目录不存在，请确保模型文件已下载"
        exit 1
    fi
    
    # 检查可用模型 (支持符号链接)
    models_found=0
    for model in "MiniCPM-V-4-int4" "MiniCPM-V-4_5-int4"; do
        if [ -L "models/$model" ]; then
            # 是符号链接，检查链接目标路径
            target=$(readlink "models/$model")
            if [[ "$target" == *"huggingface/hub/models--openbmb--"* ]]; then
                log_success "找到模型 (符号链接): $model -> $(basename "$target")"
                ((models_found++))
            else
                log_warning "模型符号链接目标异常: $model -> $target"
            fi
        elif [ -d "models/$model" ]; then
            # 是普通目录
            log_success "找到模型: $model"
            ((models_found++))
        fi
    done
    
    if [ $models_found -eq 0 ]; then
        log_error "未找到任何可用的模型文件"
        log_info "当前models目录内容:"
        ls -la models/ || true
        exit 1
    fi
    
    log_success "模型检查完成，找到 $models_found 个模型"
}

# 选择部署模式
select_mode() {
    echo
    log_info "请选择部署模式:"
    echo "1) 开发环境 (默认)"
    echo "2) 生产环境"
    echo "3) 生产环境 + Nginx反向代理"
    read -p "请输入选择 [1-3]: " mode_choice
    
    case $mode_choice in
        2)
            COMPOSE_FILE="docker/docker-compose.prod.yml"
            MODE="生产环境"
            ;;
        3)
            COMPOSE_FILE="docker/docker-compose.prod.yml"
            MODE="生产环境 + Nginx"
            NGINX_PROFILE="--profile with-nginx"
            ;;
        *)
            COMPOSE_FILE="docker/docker-compose.yml"
            MODE="开发环境"
            ;;
    esac
    
    log_info "选择的部署模式: $MODE"
}

# 配置环境变量
setup_env() {
    log_info "配置环境变量..."
    
    if [ ! -f ".env" ]; then
        log_info "创建.env文件..."
        cat > .env << EOF
# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8207
HOST_PORT=8207

# 模型配置
MODEL_PATH=./models

# 日志级别
LOG_LEVEL=INFO
EOF
    fi
    
    log_success "环境变量配置完成"
}

# 构建和启动服务
deploy_service() {
    log_info "开始部署服务..."
    
    # 停止现有服务
    log_info "停止现有服务..."
    docker-compose -f $COMPOSE_FILE down 2>/dev/null || true
    
    # 构建镜像
    log_info "构建Docker镜像..."
    docker-compose -f $COMPOSE_FILE build
    
    # 启动服务
    log_info "启动服务..."
    docker-compose -f $COMPOSE_FILE up -d $NGINX_PROFILE
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        log_success "服务启动成功!"
    else
        log_error "服务启动失败"
        docker-compose -f $COMPOSE_FILE logs
        exit 1
    fi
}

# 测试部署
test_deployment() {
    log_info "测试部署..."
    
    # 等待服务完全启动
    sleep 5
    
    # 测试健康检查
    PORT=${HOST_PORT:-8207}
    if curl -f "http://localhost:$PORT/health" &>/dev/null; then
        log_success "健康检查通过"
    else
        log_error "健康检查失败"
        return 1
    fi
    
    # 测试模型列表
    if curl -s "http://localhost:$PORT/models" | grep -q "count"; then
        log_success "模型API正常"
    else
        log_error "模型API异常"
        return 1
    fi
    
    log_success "部署测试完成"
}

# 显示部署信息
show_deployment_info() {
    PORT=${HOST_PORT:-8207}
    echo
    log_success "=== 部署完成 ==="
    echo
    echo "服务地址:"
    echo "  - API文档: http://localhost:$PORT/docs"
    echo "  - 健康检查: http://localhost:$PORT/health"
    echo "  - 模型列表: http://localhost:$PORT/models"
    echo
    echo "常用命令:"
    echo "  - 查看状态: docker-compose -f $COMPOSE_FILE ps"
    echo "  - 查看日志: docker-compose -f $COMPOSE_FILE logs -f"
    echo "  - 停止服务: docker-compose -f $COMPOSE_FILE down"
    echo "  - 重启服务: docker-compose -f $COMPOSE_FILE restart"
    echo
    if [ "$MODE" == "生产环境 + Nginx" ]; then
        echo "Nginx代理地址: http://localhost"
    fi
}

# 主函数
main() {
    echo
    log_info "=== MiniCPM-V服务器部署脚本 ==="
    echo
    
    check_dependencies
    check_models
    select_mode
    setup_env
    deploy_service
    
    if test_deployment; then
        show_deployment_info
    else
        log_error "部署测试失败，请检查日志"
        docker-compose -f $COMPOSE_FILE logs
        exit 1
    fi
}

# 错误处理
trap 'log_error "部署过程中发生错误"; exit 1' ERR

# 执行主函数
main "$@"