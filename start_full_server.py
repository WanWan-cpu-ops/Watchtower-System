#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能瞭望系统 完整服务器启动脚本
同时启动 HTTP 服务器和 WebSocket 服务器
"""

import sys
import os
import asyncio
import http.server
import socketserver
import threading

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# HTTP 服务器配置
HTTP_PORT = 8080
HTTP_DIRECTORY = os.path.join(project_root, 'client')

# WebSocket 服务器配置
WS_HOST = 'localhost'
WS_PORT = 8000

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    自定义 HTTP 请求处理程序，确保静态文件从正确的目录加载
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=HTTP_DIRECTORY, **kwargs)

class HTTPThread(threading.Thread):
    """
    用于在单独线程中运行 HTTP 服务器的类
    """
    def __init__(self):
        threading.Thread.__init__(self)
        
        # 创建 HTTP 服务器，使用自定义请求处理程序
        self.httpd = socketserver.TCPServer(("", HTTP_PORT), HTTPRequestHandler)
        
        print(f"HTTP 服务器配置完成，端口: {HTTP_PORT}")
        print(f"静态文件目录: {HTTP_DIRECTORY}")
        print(f"访问地址: http://localhost:{HTTP_PORT}/login.html")
    
    def run(self):
        """
        运行 HTTP 服务器
        """
        print(f"HTTP 服务器已启动，端口: {HTTP_PORT}")
        self.httpd.serve_forever()
    
    def stop(self):
        """
        停止 HTTP 服务器
        """
        self.httpd.shutdown()
        print(f"HTTP 服务器已停止")

async def start_websocket_server():
    """
    启动 WebSocket 服务器
    """
    try:
        # 将工作目录改回项目根目录
        os.chdir(project_root)
        
        # 导入 WebSocket 服务器模块
        from server.websocket_server import WebSocketServer
        
        # 创建 WebSocket 服务器
        server = WebSocketServer(host=WS_HOST, port=WS_PORT)
        print(f"WebSocket 服务器配置完成，地址: ws://{server.host}:{server.port}")
        
        # 启动 WebSocket 服务器
        await server.start_server()
        
    except ImportError as e:
        print(f"导入 WebSocket 服务器模块失败: {e}")
        print("请确保所有依赖项都已安装")
    except Exception as e:
        print(f"启动 WebSocket 服务器失败: {e}")

async def main():
    """
    主函数，启动 HTTP 服务器和 WebSocket 服务器
    """
    try:
        # 启动 HTTP 服务器（在单独线程中）
        http_thread = HTTPThread()
        http_thread.start()
        
        # 启动 WebSocket 服务器
        await start_websocket_server()
        
    except KeyboardInterrupt:
        print("\n收到中断信号，正在停止所有服务器...")
        
        # 停止 HTTP 服务器
        if 'http_thread' in locals():
            http_thread.stop()
            http_thread.join()
        
        print("所有服务器已停止")
    except Exception as e:
        print(f"启动服务器失败: {e}")

if __name__ == "__main__":
    print("智能瞭望系统 完整服务器启动程序")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"程序运行失败: {e}")