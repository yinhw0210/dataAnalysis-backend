#!/bin/bash

# 部署脚本 - 在生产服务器上部署应用
# 使用方法: ./deploy.sh [port]

# 设置错误时退出
set -e

# 定义日志函数
log_info() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") [INFO] $1"
}

log_warn() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") [WARN] $1"
}

log_error() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") [ERROR] $1"
}

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 默认端口
PORT=${1:-8000}
HOST=${2:-0.0.0.0}

# 确保日志目录存在
mkdir -p logs

# 显示版本信息
echo "===== 部署数据分析 API 服务 ====="
python --version
echo "当前目录: $(pwd)"

# 如果存在虚拟环境，则激活
if [ -d ".venv" ]; then
    echo "激活虚拟环境..."
    source .venv/bin/activate
fi
# 不存在的话创建一个
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python -m venv .venv
    source .venv/bin/activate
fi

# 拉取最新代码
echo "拉取最新代码..."
git pull

# 安装/更新依赖
echo "安装/更新依赖..."
pip install -r requirements.txt

# 检查是否有旧的进程在运行
if [ -f "logs/server.pid" ]; then
    OLD_PID=$(cat logs/server.pid)
    if ps -p $OLD_PID > /dev/null; then
        echo "停止旧进程 (PID: $OLD_PID)..."
        kill $OLD_PID || true
        sleep 2
    fi
fi

# 获取当前日期和时间
DATE=$(date +"%Y-%m-%d_%H-%M-%S")

# 设置环境变量
export APP_ENV="production"
export PORT="$PORT"
export HOST="$HOST"

echo "以生产模式启动服务，主机: $HOST，端口: $PORT..."
# 启动服务
nohup python start_server.py --env production --port $PORT --host $HOST > "logs/deploy_${DATE}.log" 2>&1 &

# 保存进程 ID
PID=$!
echo $PID > logs/server.pid
echo "服务已启动，PID: $PID"
echo "日志保存在 logs 目录下"

# 等待服务启动
echo "等待服务启动..."
sleep 3

# 检查服务是否正常运行
if ps -p $PID > /dev/null; then
    echo "服务启动成功！"
    echo "API 可访问于: http://$HOST:$PORT"
    echo "API 文档可访问于: http://$HOST:$PORT/docs"
else
    echo "服务启动失败，请检查日志"
    exit 1
fi

echo "部署完成！"