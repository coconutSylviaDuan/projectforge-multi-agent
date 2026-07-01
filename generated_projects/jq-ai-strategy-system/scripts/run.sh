#!/bin/bash
# AI Strategy System - 一键本地启动脚本
# 适用于 Linux / macOS

set -e

echo "===== AI 策略系统 - 本地启动 ====="

# 1. 后端启动
echo "[1/4] 配置后端虚拟环境..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "[2/4] 安装后端依赖..."
pip install -r requirements.txt --quiet

echo "[3/4] 初始化数据库..."
python -c "from app.database import init_db; init_db()"

echo "[4/4] 启动后端服务 (端口 8000)..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

echo "后端进程 PID: $BACKEND_PID"

# 2. 前端启动
echo "启动前端服务 (端口 5173)..."
cd frontend
python3 -m http.server 5173 --directory . &
FRONTEND_PID=$!
cd ..

echo "前端进程 PID: $FRONTEND_PID"

echo ""
echo "===== 启动完成 ====="
echo "前端地址: http://localhost:5173"
echo "后端地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo "按 Ctrl+C 停止所有服务"

# 等待子进程
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
