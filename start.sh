#!/bin/bash

# 启动脚本 for 智能瞭望数据分析处理系统

echo "========================================"
echo "      智能瞭望数据分析处理系统"
echo "========================================"
echo ""

# 检查是否在项目目录中
if [ ! -d "server" ] || [ ! -d "clients" ]; then
    echo "错误：请在项目根目录下运行此脚本"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "未检测到虚拟环境，正在创建..."
    python -m venv venv
    if [ $? -ne 0 ]; then
        echo "创建虚拟环境失败，请检查Python安装"
        exit 1
    fi
    echo "虚拟环境创建成功！"
fi

# 激活虚拟环境
echo "正在激活虚拟环境..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "无法找到虚拟环境激活脚本"
    exit 1
fi

echo "虚拟环境已激活！"

# 安装依赖
echo "正在检查依赖..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "安装依赖失败"
    exit 1
fi

echo "依赖安装完成！"

# 检查数据库是否存在
if [ ! -f "server/database.db" ]; then
    echo "数据库不存在，正在初始化..."
    python server/init_db.py
    if [ $? -ne 0 ]; then
        echo "数据库初始化失败"
        exit 1
    fi
    echo "数据库初始化完成！"
fi

# 启动WebSocket服务器
echo "正在启动WebSocket服务器..."
python server/websocket_server.py &
SERVER_PID=$!

# 等待服务器启动
sleep 2

# 检查服务器是否启动成功
if ! ps -p $SERVER_PID > /dev/null; then
    echo "服务器启动失败，请检查日志"
    exit 1
fi

echo "WebSocket服务器已启动在 ws://localhost:8765"
echo ""
echo "========================================"
echo "应用已成功启动！"
echo "请在浏览器中访问: http://localhost:8000/clients/html/index.html"
echo "========================================"
echo ""
echo "按 Ctrl+C 停止服务器"

# 启动HTTP服务器（用于提供静态文件）
python -m http.server 8000

# 停止WebSocket服务器
kill $SERVER_PID

echo "服务器已停止"