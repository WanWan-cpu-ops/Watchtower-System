@echo off

REM 启动脚本 for 智能瞭望数据分析处理系统

echo ========================================
echo       智能瞭望数据分析处理系统
echo ========================================
echo.

REM 检查是否在项目目录中
if not exist "server" (goto error_dir)
if not exist "clients" (goto error_dir)

REM 检查虚拟环境是否存在
if not exist "venv" (
    echo 未检测到虚拟环境，正在创建...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (goto error_venv)
    echo 虚拟环境创建成功！
)

REM 激活虚拟环境
echo 正在激活虚拟环境...
call venv\Scripts\activate
if %ERRORLEVEL% neq 0 (goto error_activate)

echo 虚拟环境已激活！

REM 安装依赖
echo 正在检查依赖...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (goto error_pip)

echo 依赖安装完成！

REM 检查数据库是否存在
if not exist "server\database.db" (
    echo 数据库不存在，正在初始化...
    python server\init_db.py
    if %ERRORLEVEL% neq 0 (goto error_db)
    echo 数据库初始化完成！
)

REM 启动WebSocket服务器
echo 正在启动WebSocket服务器...
start "WebSocket Server" python server\websocket_server.py

REM 等待服务器启动
timeout /t 2 /nobreak >nul

REM 启动HTTP服务器（用于提供静态文件）
echo 正在启动HTTP服务器...
echo.
echo ========================================
echo 应用已成功启动！
echo 请在浏览器中访问: http://localhost:8000/clients/html/index.html
echo ========================================
echo.
echo 按 Ctrl+C 停止服务器

python -m http.server 8000

REM 清理工作
echo.
echo 正在关闭服务器...
taskkill /FI "WINDOWTITLE eq WebSocket Server" /F >nul 2>&1

echo 服务器已停止
pause
goto end

:error_dir
echo 错误：请在项目根目录下运行此脚本
pause
goto end

:error_venv
echo 创建虚拟环境失败，请检查Python安装
pause
goto end

:error_activate
echo 无法激活虚拟环境
pause
goto end

:error_pip
echo 安装依赖失败
pause
goto end

:error_db
echo 数据库初始化失败
pause
goto end

:end