import asyncio
import websockets
import sqlite3
import bcrypt
import os
import sys
import importlib.util
import threading
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from C2SPackageHelper import C2SPackageHelper

# 搜索源目录
SEARCH_SOURCES_DIR = "../search_sources"

# 客户端连接存储
clients = set()
# 缓存搜索结果
search_results_cache = {}

class WebSocketServer:
    """WebSocket服务器主类"""
    
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.db_conn = None
        self.db_cursor = None
        
        # 初始化数据库连接
        self.init_db()
        
        # 初始化搜索源
        self.refresh_search_sources()
    
    def init_db(self):
        """初始化数据库连接"""
        self.db_conn = sqlite3.connect('telescope.db', check_same_thread=False)
        self.db_cursor = self.db_conn.cursor()
    
    def refresh_search_sources(self):
        """刷新搜索源列表，将搜索源目录中的所有Python文件注册到数据库"""
        if not os.path.exists(SEARCH_SOURCES_DIR):
            return
            
        # 获取所有Python文件
        python_files = [f for f in os.listdir(SEARCH_SOURCES_DIR) if f.endswith('.py')]
        
        for filename in python_files:
            # 提取搜索源名称（不带.py扩展名）
            name = filename[:-3]
            
            # 检查是否已存在
            self.db_cursor.execute("SELECT id FROM search_sources WHERE filename = ?", (filename,))
            if not self.db_cursor.fetchone():
                # 插入新的搜索源
                self.db_cursor.execute(
                    "INSERT INTO search_sources (name, filename) VALUES (?, ?)",
                    (name, filename)
                )
        
        self.db_conn.commit()
    
    async def handle_client(self, websocket):
        """处理客户端连接"""
        clients.add(websocket)
        
        try:
            async for message in websocket:
                print(f"[{datetime.now()}] 收到客户端消息: {message}")
                # 解析客户端消息
                package = C2SPackageHelper.parse_package(message)
                msg_type = package.get("msg_type")
                data = package.get("data", {})
                
                # 根据消息类型处理
                if msg_type == C2SPackageHelper.MSG_TYPE_LOGIN:
                    await self.handle_login(websocket, data)
                elif msg_type == C2SPackageHelper.MSG_TYPE_REGISTER:
                    await self.handle_register(websocket, data)
                elif msg_type == C2SPackageHelper.MSG_TYPE_SEARCH:
                    await self.handle_search(websocket, data)
                elif msg_type == C2SPackageHelper.MSG_TYPE_FILTER:
                    await self.handle_filter(websocket, data)
                elif msg_type == C2SPackageHelper.MSG_TYPE_REFRESH_DATA:
                    await self.handle_refresh_data(websocket, data)
                elif msg_type == C2SPackageHelper.MSG_TYPE_DELETE_DATA:
                    await self.handle_delete_data(websocket, data)
                elif msg_type == C2SPackageHelper.MSG_TYPE_REFRESH_SOURCES:
                    await self.handle_refresh_sources(websocket)
                elif msg_type == C2SPackageHelper.MSG_TYPE_TOGGLE_SOURCE:
                    await self.handle_toggle_source(websocket, data)
                elif msg_type == C2SPackageHelper.MSG_TYPE_SEND_VERIFICATION_CODE:
                    await self.handle_send_verification_code(websocket, data)
                elif msg_type == C2SPackageHelper.MSG_TYPE_SUBMIT_VERIFICATION:
                    await self.handle_submit_verification(websocket, data)
                elif msg_type == C2SPackageHelper.MSG_TYPE_REFRESH_PROFILE:
                    await self.handle_refresh_profile(websocket, data)
        
        finally:
            clients.remove(websocket)
    
    async def handle_login(self, websocket, data):
        """处理用户登录"""
        username = data.get("username")
        password = data.get("password")
        
        # 验证用户名和密码
        self.db_cursor.execute("SELECT id, password, permission_level FROM users WHERE username = ?", (username,))
        user = self.db_cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            # 登录成功
            user_info = {
                "username": username,
                "permission_level": user[2]
            }
            response = C2SPackageHelper.create_login_response(C2SPackageHelper.STATUS_SUCCESS, user_info)
        else:
            # 登录失败
            response = C2SPackageHelper.create_login_response(C2SPackageHelper.STATUS_FAILED)
        
        print(f"[{datetime.now()}] 发送登录响应: {response}")
        await websocket.send(response)
    
    async def handle_register(self, websocket, data):
        """处理用户注册"""
        print("收到注册请求:", data)
        
        username = data.get("username")
        password = data.get("password")
        
        # 检查用户名是否已存在
        self.db_cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if self.db_cursor.fetchone():
            # 用户名已存在
            print("用户名已存在:", username)
            response = C2SPackageHelper.create_register_response(
                C2SPackageHelper.STATUS_FAILED,
                {"message": "用户名已存在"}
            )
        else:
            # 创建新用户
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.db_cursor.execute(
                "INSERT INTO users (username, password, permission_level) VALUES (?, ?, ?)",
                (username, hashed_password, 0)  # 默认权限级别为0
            )
            self.db_conn.commit()
            print("注册成功:", username)
            
            # 注册成功
            response = C2SPackageHelper.create_register_response(
                C2SPackageHelper.STATUS_SUCCESS
            )
        
        print(f"[{datetime.now()}] 发送注册响应: {response}")
        await websocket.send(response)
    
    async def handle_search(self, websocket, data):
        """处理数据搜索请求"""
        search_content = data.get("search_content")
        page_count = data.get("page_count", 1)
        
        # 发送正在搜索信号
        processing_response = C2SPackageHelper.create_search_response(C2SPackageHelper.STATUS_PROCESSING)
        print(f"[{datetime.now()}] 发送搜索处理响应: {processing_response}")
        await websocket.send(processing_response)
        
        # 获取所有可用搜索源
        self.db_cursor.execute("SELECT id, name, filename FROM search_sources WHERE is_blacklisted = 0")
        sources = self.db_cursor.fetchall()
        
        all_results = []
        
        # 调用所有搜索源
        for source_id, source_name, filename in sources:
            result = self.run_search_source(filename, search_content, page_count)
            if result["status"] == "success":
                # 为每个结果添加来源标识
                for item in result["data"]:
                    item["source"] = source_name
                all_results.extend(result["data"])
        
        # 缓存搜索结果
        search_id = f"search_{datetime.now().timestamp()}"
        search_results_cache[search_id] = all_results
        
        # 发送搜索完成信号和结果
        response_data = {
            "search_id": search_id,
            "results": all_results
        }
        search_response = C2SPackageHelper.create_search_response(
            C2SPackageHelper.STATUS_COMPLETED, response_data
        )
        print(f"[{datetime.now()}] 发送搜索完成响应: {search_response}")
        await websocket.send(search_response)
    
    def run_search_source(self, filename, search_content, page_count):
        """运行搜索源脚本"""
        try:
            # 动态导入搜索源模块
            module_path = os.path.join(SEARCH_SOURCES_DIR, filename)
            spec = importlib.util.spec_from_file_location(filename[:-3], module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 调用main函数
            if hasattr(module, "main"):
                status, data = module.main(search_content, page_count)
                return {
                    "status": status,
                    "data": data
                }
            else:
                return {
                    "status": "failed",
                    "data": []
                }
        except Exception as e:
            print(f"搜索源 {filename} 执行失败: {e}")
            return {
                "status": "failed",
                "data": []
            }
    
    async def handle_filter(self, websocket, data):
        """处理数据筛选请求"""
        search_id = data.get("search_id")
        selected_ids = data.get("selected_ids", [])
        
        # 验证搜索ID和选中的ID
        if search_id not in search_results_cache:
            await websocket.send(C2SPackageHelper.create_filter_response(C2SPackageHelper.STATUS_FAILED))
            return
        
        # 发送筛选接收成功信号
        filter_received_response = C2SPackageHelper.create_filter_response(C2SPackageHelper.STATUS_RECEIVED)
        print(f"[{datetime.now()}] 发送筛选接收响应: {filter_received_response}")
        await websocket.send(filter_received_response)
        
        # 将选中的数据保存到数据库
        for idx in selected_ids:
            if 0 <= idx < len(search_results_cache[search_id]):
                item = search_results_cache[search_id][idx]
                self.db_cursor.execute(
                    "INSERT INTO data_records (title, summary, image_url, url, source) VALUES (?, ?, ?, ?, ?)",
                    (item["title"], item["summary"], item["image_url"], item["url"], item["source"])
                )
        
        self.db_conn.commit()
        
        # 发送入库完成信号
        filter_completed_response = C2SPackageHelper.create_filter_response(C2SPackageHelper.STATUS_COMPLETED)
        print(f"[{datetime.now()}] 发送筛选完成响应: {filter_completed_response}")
        await websocket.send(filter_completed_response)
    
    async def handle_refresh_data(self, websocket, data):
        """处理数据管理页面刷新请求"""
        search_content = data.get("search_content", "")
        search_field = data.get("search_field", "title")
        
        # 发送正在读取信号
        data_processing_response = C2SPackageHelper.create_data_response(C2SPackageHelper.STATUS_PROCESSING)
        print(f"[{datetime.now()}] 发送数据处理响应: {data_processing_response}")
        await websocket.send(data_processing_response)
        
        # 构建查询语句
        if search_content:
            query = f"SELECT id, title, summary, image_url, url, source, created_at FROM data_records WHERE {search_field} LIKE ? ORDER BY created_at DESC"
            self.db_cursor.execute(query, (f"%{search_content}%",))
        else:
            self.db_cursor.execute("SELECT id, title, summary, image_url, url, source, created_at FROM data_records ORDER BY created_at DESC")
        
        records = self.db_cursor.fetchall()
        
        # 格式化数据
        formatted_records = []
        for record in records:
            formatted_records.append({
                "id": record[0],
                "title": record[1],
                "summary": record[2],
                "image_url": record[3],
                "url": record[4],
                "source": record[5],
                "created_at": record[6]
            })
        
        # 发送数据完成信号和记录
        data_response = C2SPackageHelper.create_data_response(
            C2SPackageHelper.STATUS_COMPLETED, formatted_records
        )
        print(f"[{datetime.now()}] 发送数据完成响应: {data_response}")
        await websocket.send(data_response)
    
    async def handle_delete_data(self, websocket, data):
        """处理数据删除请求"""
        record_ids = data.get("record_ids", [])
        
        # 发送正在删除信号
        delete_processing_response = C2SPackageHelper.create_data_response(C2SPackageHelper.STATUS_PROCESSING)
        print(f"[{datetime.now()}] 发送删除处理响应: {delete_processing_response}")
        await websocket.send(delete_processing_response)
        
        # 删除选中的数据
        if record_ids:
            placeholders = ",".join(["?"] * len(record_ids))
            query = f"DELETE FROM data_records WHERE id IN ({placeholders})"
            self.db_cursor.execute(query, record_ids)
            self.db_conn.commit()
        
        # 发送删除完成信号
        delete_completed_response = C2SPackageHelper.create_data_response(C2SPackageHelper.STATUS_COMPLETED)
        print(f"[{datetime.now()}] 发送删除完成响应: {delete_completed_response}")
        await websocket.send(delete_completed_response)
        
        # 重新读取数据
        await self.handle_refresh_data(websocket, {})
    
    async def handle_refresh_sources(self, websocket):
        """处理搜索源管理页面刷新请求"""
        # 发送正在寻找搜索源信号
        source_processing_response = C2SPackageHelper.create_source_response(C2SPackageHelper.STATUS_PROCESSING)
        print(f"[{datetime.now()}] 发送搜索源处理响应: {source_processing_response}")
        await websocket.send(source_processing_response)
        
        # 获取所有搜索源
        self.db_cursor.execute("SELECT id, name, filename, is_blacklisted FROM search_sources")
        sources = self.db_cursor.fetchall()
        
        # 格式化数据
        formatted_sources = []
        for source in sources:
            formatted_sources.append({
                "id": source[0],
                "name": source[1],
                "filename": source[2],
                "is_blacklisted": bool(source[3])
            })
        
        # 发送搜索源寻找完成信号和数据
        source_response = C2SPackageHelper.create_source_response(
            C2SPackageHelper.STATUS_COMPLETED, formatted_sources
        )
        print(f"[{datetime.now()}] 发送搜索源完成响应: {source_response}")
        await websocket.send(source_response)
    
    async def handle_toggle_source(self, websocket, data):
        """处理搜索源启用/禁用请求"""
        source_id = data.get("source_id")
        is_blacklisted = data.get("is_blacklisted")
        
        # 更新搜索源状态
        self.db_cursor.execute(
            "UPDATE search_sources SET is_blacklisted = ? WHERE id = ?",
            (1 if is_blacklisted else 0, source_id)
        )
        self.db_conn.commit()
        
        # 重新读取搜索源
        await self.handle_refresh_sources(websocket)
        
    async def handle_send_verification_code(self, websocket, data):
        """处理发送验证码请求"""
        phone_number = data.get("phone_number")
        
        # 这里应该实现真实的验证码发送逻辑
        # 由于是模拟环境，我们直接返回成功
        
        sms_response = C2SPackageHelper.create_sms_response(
            C2SPackageHelper.STATUS_SUCCESS, {
                "message": "验证码发送成功"
            }
        )
        await websocket.send(sms_response)
        
    async def handle_submit_verification(self, websocket, data):
        """处理提交实名认证信息请求"""
        real_name = data.get("real_name")
        id_card = data.get("id_card")
        phone_number = data.get("phone_number")
        verification_code = data.get("verification_code")
        request_id = data.get("request_id")
        username = data.get("username")
        
        # 这里应该实现真实的验证码验证和实名认证逻辑
        # 由于是模拟环境，我们直接将状态设置为"审核中"
        
        # 获取当前用户
        username = self.current_users.get(websocket)
        if username:
            # 更新用户实名认证信息
            self.db_cursor.execute("""
                UPDATE users 
                SET real_name = ?, id_card = ?, phone_number = ?, verification_status = 1
                WHERE username = ?
            """, (real_name, id_card, phone_number, username))
            self.db_conn.commit()
            
            verification_response = C2SPackageHelper.create_verification_response(
                C2SPackageHelper.STATUS_SUCCESS, {
                    "message": "实名认证提交成功，正在审核中"
                }
            )
            await websocket.send(verification_response)
    
    async def handle_refresh_profile(self, websocket, data):
        """处理个人资料刷新请求"""
        username = data.get("username")
        
        # 获取用户信息（包括实名认证相关字段）
        self.db_cursor.execute("SELECT username, permission_level, real_name, id_card, phone_number, verification_status, verification_reason FROM users WHERE username = ?", (username,))
        user = self.db_cursor.fetchone()
        
        if user:
            profile_data = {
                "username": user[0],
                "permission_level": user[1],
                "real_name": user[2],
                "id_card": user[3],
                "phone_number": user[4],
                "verification_status": user[5] or 0,
                "verification_reason": user[6]
            }
            profile_response = C2SPackageHelper.create_profile_response(
                C2SPackageHelper.STATUS_COMPLETED, profile_data
            )
            print(f"[{datetime.now()}] 发送个人资料响应: {profile_response}")
            await websocket.send(profile_response)
        else:
            profile_response = C2SPackageHelper.create_profile_response(C2SPackageHelper.STATUS_FAILED)
            print(f"[{datetime.now()}] 发送个人资料响应: {profile_response}")
            await websocket.send(profile_response)
    
    async def start_server(self):
        """启动WebSocket服务器"""
        async with websockets.serve(lambda ws: self.handle_client(ws), self.host, self.port):
            print(f"WebSocket服务器已启动，监听 {self.host}:{self.port}")
            await asyncio.Future()  # 保持服务器运行

def main():
    """主函数"""
    server = WebSocketServer()
    asyncio.run(server.start_server())

if __name__ == "__main__":
    main()