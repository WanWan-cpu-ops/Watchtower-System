#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能瞭望系统 启动脚本

该脚本用于启动智能瞭望系统的服务器组件，包括 WebSocket 服务器和 HTTP 服务器。
"""

import sys
import os
import asyncio

# 检查是否在虚拟环境中运行
if not hasattr(sys, 'base_prefix') or sys.base_prefix == sys.prefix:
    print("错误: 该应用程序必须在虚拟环境中运行!")
    print("请先激活虚拟环境，然后再运行此脚本:")
    print("Windows: venv\\Scripts\\activate.bat")
    print("Linux/Mac: source venv/bin/activate")
    sys.exit(1)

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """启动服务器"""
    try:
        # 导入WebSocket服务器模块
        from server.websocket_server import WebSocketServer
        
        # 创建并启动WebSocket服务器
        server = WebSocketServer(host='localhost', port=8080)
        print("智能瞭望系统 服务器已启动")
        print(f"WebSocket地址: ws://{server.host}:{server.port}")
        print("按 Ctrl+C 停止服务器")
        
        # 启动服务器
        asyncio.run(server.start_server())
        
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保所有依赖项都已安装")
    except Exception as e:
        print(f"启动服务器失败: {e}")

if __name__ == "__main__":
    main()