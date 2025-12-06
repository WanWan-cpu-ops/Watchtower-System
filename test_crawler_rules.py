import asyncio
import websockets
import json
import time

async def test_crawler_rules():
    # 连接到WebSocket服务器
    uri = "ws://localhost:8000"
    async with websockets.connect(uri) as websocket:
        print("连接到服务器成功")
        
        # 1. 测试嗅探功能
        print("\n1. 测试嗅探功能...")
        sniff_data = {
            "type": "sniff_webpage",
            "data": {
                "url": "https://www.example.com",
                "source_id": "example",
                "source_name": "Example Website",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
            }
        }
        
        # 打印发送的消息
        print(f"发送的消息: {json.dumps(sniff_data, ensure_ascii=False)}")
        await websocket.send(json.dumps(sniff_data))
        
        try:
            # 等待响应，设置超时
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            print(f"嗅探响应: {response}")
            
            # 解析响应
            response_data = json.loads(response)
            print(f"响应类型: {response_data.get('type')}")
            print(f"响应数据: {json.dumps(response_data.get('data', {}), ensure_ascii=False)}")
        except asyncio.TimeoutError:
            print("错误：等待响应超时")
        except Exception as e:
            print(f"错误：{str(e)}")
        
        # 2. 测试保存爬虫规则
        print("\n2. 测试保存爬虫规则...")
        save_data = {
            "type": "save_crawler_rule",
            "data": {
                "source_id": "example",
                "source_name": "Example Website",
                "title_xpath": "//h1",
                "content_xpath": "//div[@class='content']",
                "image_xpath": "//img",
                "url_xpath": "//a[@href]",
                "request_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
                "status": 1,
                "remarks": "测试规则"
            }
        }
        await websocket.send(json.dumps(save_data))
        
        # 接收正在保存响应
        response = await websocket.recv()
        print(f"正在保存响应: {response}")
        
        # 接收保存完成响应
        response = await websocket.recv()
        print(f"保存完成响应: {response}")
        
        # 解析响应获取规则ID
        response_data = json.loads(response)
        rule_id = None
        if response_data.get("type") == "crawler_rule_saved" and "data" in response_data:
            rule_id = response_data["data"].get("rule_id")
        
        # 3. 测试获取爬虫规则列表
        print("\n3. 测试获取爬虫规则列表...")
        refresh_data = {
            "type": "refresh_crawler_rules"
        }
        await websocket.send(json.dumps(refresh_data))
        
        response = await websocket.recv()
        print(f"刷新规则列表响应: {response}")
        
        # 4. 如果有规则ID，测试启用/禁用和删除功能
        if rule_id:
            # 测试禁用爬虫规则
            print("\n4. 测试禁用爬虫规则...")
            disable_data = {
                "type": "disable_crawler_rule",
                "data": {
                    "rule_id": rule_id
                }
            }
            await websocket.send(json.dumps(disable_data))
            
            response = await websocket.recv()
            print(f"禁用规则响应: {response}")
            
            # 测试启用爬虫规则
            print("\n5. 测试启用爬虫规则...")
            enable_data = {
                "type": "enable_crawler_rule",
                "data": {
                    "rule_id": rule_id
                }
            }
            await websocket.send(json.dumps(enable_data))
            
            response = await websocket.recv()
            print(f"启用规则响应: {response}")
            
            # 测试删除爬虫规则
            print("\n6. 测试删除爬虫规则...")
            delete_data = {
                "type": "delete_crawler_rule",
                "data": {
                    "rule_id": rule_id
                }
            }
            await websocket.send(json.dumps(delete_data))
            
            response = await websocket.recv()
            print(f"删除规则响应: {response}")

if __name__ == "__main__":
    asyncio.run(test_crawler_rules())