#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试request header嗅探功能的脚本
"""

import asyncio
import websockets
import json

async def test_sniff_rules():
    # WebSocket服务器地址
    uri = "ws://localhost:8080"
    
    async with websockets.connect(uri) as websocket:
        # 登录请求
        login_data = {
            "type": "login",
            "data": {
                "username": "admin",
                "password": "admin"
            }
        }
        
        await websocket.send(json.dumps(login_data))
        login_response = await websocket.recv()
        print("登录响应:", login_response)
        
        # 测试嗅探规则请求
        sniff_data = {
            "type": "sniff_rules",
            "data": {
                "source_url": "https://example.com",
                "target_title": "Example Domain"
            }
        }
        
        await websocket.send(json.dumps(sniff_data))
        sniff_response = await websocket.recv()
        print("嗅探规则响应:", sniff_response)
        
        # 解析响应
        response_data = json.loads(sniff_response)
        if response_data.get("success"):
            rules = response_data.get("data", {}).get("rules")
            if rules:
                print("\n嗅探到的规则:")
                print(f"源URL: {rules.get('source_url')}")
                print(f"域名: {rules.get('domain')}")
                print(f"标题XPath: {rules.get('title_xpath')}")
                print(f"内容XPath: {rules.get('content_xpath')}")
                print(f"图片XPath: {rules.get('image_xpath')}")
                print(f"请求头: {rules.get('request_headers')}")

if __name__ == "__main__":
    asyncio.run(test_sniff_rules())