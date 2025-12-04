import asyncio
import websockets
import json
import time
from datetime import datetime
from .database import Database
from .C2SPackageHelper import C2SPackageHelper
from .search_source_manager import SearchSourceManager

class WebSocketServer:
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.clients = set()
        
        # 初始化数据库和搜索源管理器
        self.db = Database()
        self.search_source_manager = SearchSourceManager(self.db.get_blacklist())
        
        # 保存最后一次搜索的结果
        self.last_search_results = []
        
    def log(self, message, level='INFO'):
        """
        日志记录函数
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    async def handle_client(self, websocket):
        """
        处理客户端连接
        """
        self.clients.add(websocket)
        self.log(f"新客户端连接: {websocket.remote_address}", 'INFO')
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        
        except websockets.exceptions.ConnectionClosedError as e:
            self.log(f"客户端连接关闭: {websocket.remote_address} - 错误: {e}", 'WARNING')
        
        except Exception as e:
            self.log(f"客户端连接异常: {websocket.remote_address} - 错误: {e}", 'ERROR')
        
        finally:
            self.clients.remove(websocket)
            self.log(f"客户端已断开: {websocket.remote_address}", 'INFO')
    
    async def process_message(self, websocket, message):
        """
        处理客户端发送的消息
        """
        try:
            self.log(f"接收到客户端消息: {message} from {websocket.remote_address}", 'DEBUG')
            data = json.loads(message)
            message_type = data.get('type')
            message_data = data.get('data', {})
            
            self.log(f"处理消息: 类型={message_type}, 数据={message_data} from {websocket.remote_address}", 'INFO')
            
            # 根据消息类型处理
            if message_type == 'login':
                await self.handle_login(websocket, message_data)
            
            elif message_type == 'search_data':
                await self.handle_search_data(websocket, message_data)
            
            elif message_type == 'filter_data':
                await self.handle_filter_data(websocket, message_data)
            
            elif message_type == 'refresh_data_management':
                await self.handle_refresh_data_management(websocket)
            
            elif message_type == 'delete_data':
                await self.handle_delete_data(websocket, message_data)
            
            elif message_type == 'refresh_search_source_management':
                await self.handle_refresh_search_source_management(websocket)
            
            elif message_type == 'disable_search_source':
                await self.handle_disable_search_source(websocket, message_data)
            
            elif message_type == 'enable_search_source':
                await self.handle_enable_search_source(websocket, message_data)
            
            else:
                self.log(f"未知消息类型: {message_type} from {websocket.remote_address}", 'WARNING')
                await websocket.send(C2SPackageHelper.error("未知消息类型"))
        
        except json.JSONDecodeError as e:
            self.log(f"无效的JSON消息: {message} from {websocket.remote_address} - 错误: {e}", 'ERROR')
            await websocket.send(C2SPackageHelper.error("无效的JSON消息"))
        
        except Exception as e:
            self.log(f"处理消息时发生错误: {str(e)} from {websocket.remote_address}", 'ERROR')
            await websocket.send(C2SPackageHelper.error(f"服务器错误: {str(e)}"))
    
    # 处理登录
    async def handle_login(self, websocket, data):
        username = data.get('username')
        password = data.get('password')
        
        self.log(f"开始处理登录请求: 用户名={username} from {websocket.remote_address}", 'INFO')
        self.log(f"数据库文件路径: {self.db.db_path}", 'DEBUG')
        
        if not username or not password:
            self.log(f"登录失败: 用户名或密码为空 - 用户名={username}, 密码={password}", 'WARNING')
            await websocket.send(C2SPackageHelper.login_failure("用户名和密码不能为空"))
            return
        
        # 验证用户
        user = self.db.get_user(username)
        self.log(f"数据库查询结果: {user}", 'DEBUG')
        
        if user and user[2] == password:  # user[2] 是密码字段
            self.log(f"登录成功: 用户名={username}, 权限等级={user[3]}", 'INFO')
            response = C2SPackageHelper.login_success(username, user[3])
            await websocket.send(response)
            self.log(f"发送登录成功响应: {response}", 'DEBUG')
        else:
            self.log(f"登录失败: 用户名或密码错误 - 用户名={username}", 'WARNING')
            response = C2SPackageHelper.login_failure()
            await websocket.send(response)
            self.log(f"发送登录失败响应: {response}", 'DEBUG')
    
    # 处理数据搜索
    async def handle_search_data(self, websocket, data):
        search_content = data.get('search_content')
        max_pages = data.get('max_pages', 1)
        
        self.log(f"开始处理数据搜索请求: 搜索内容={search_content}, 最大页数={max_pages} from {websocket.remote_address}", 'INFO')
        
        if not search_content:
            self.log(f"搜索请求失败: 搜索内容不能为空 from {websocket.remote_address}", 'WARNING')
            response = C2SPackageHelper.error("搜索内容不能为空")
            await websocket.send(response)
            self.log(f"发送搜索失败响应: {response}", 'DEBUG')
            return
        
        # 发送正在搜索信号
        searching_response = C2SPackageHelper.searching()
        await websocket.send(searching_response)
        self.log(f"发送正在搜索响应: {searching_response}", 'DEBUG')
        
        # 获取所有启用的搜索源
        enabled_sources = self.search_source_manager.get_enabled_sources()
        self.log(f"获取到启用的搜索源: {[source['name'] for source in enabled_sources]}", 'DEBUG')
        
        # 调用所有搜索源进行搜索
        all_data = []
        for source in enabled_sources:
            try:
                self.log(f"调用搜索源: {source['name']} 搜索内容: {search_content}", 'INFO')
                # 调用搜索源的main函数
                status, data_list = source['module'].main(search_content, max_pages)
                if status and data_list:
                    self.log(f"搜索源 {source['name']} 返回数据: {len(data_list)} 条", 'INFO')
                    
                    # 处理百度爬虫返回的新数据结构
                    if source['name'] == 'baidu':
                        for search_result in data_list:
                            if 'results' in search_result:
                                for result in search_result['results']:
                                    result['data_source'] = source['name']
                                all_data.extend(search_result['results'])
                    else:
                        for result in data_list:
                            result['data_source'] = source['name']
                        all_data.extend(data_list)
                else:
                    self.log(f"搜索源 {source['name']} 未返回有效数据", 'WARNING')
            except Exception as e:
                self.log(f"搜索源 {source['name']} 调用失败: {str(e)}", 'ERROR')
        
        # 发送搜索完成信号和数据
        self.log(f"所有搜索源完成搜索，总计数据: {len(all_data)} 条", 'INFO')
        
        # 为每个结果添加唯一ID和数据源说明，并映射字段名称
        for i, result in enumerate(all_data):
            # 添加唯一ID
            result['id'] = f"{i}_{int(time.time())}"
            
            # 映射字段名称：将url和cover_url映射到source_url和image_url
            if 'url' in result:
                result['source_url'] = result['url']
            if 'cover_url' in result:
                result['image_url'] = result['cover_url']
            
            # 添加数据源说明
            if 'data_source' in result:
                source = next((s for s in self.search_source_manager.get_all_sources() if s['name'] == result['data_source']), None)
                if source:
                    result['data_source_info'] = {
                        'name': source['display_name'],
                        'description': source['description'],
                        'enabled': source['enabled']
                    }
        
        # 保存最后一次搜索的结果
        self.last_search_results = all_data
        
        completed_response = C2SPackageHelper.search_completed(all_data)
        await websocket.send(completed_response)
        self.log(f"发送搜索完成响应: {completed_response}", 'DEBUG')
    
    # 处理数据筛选（入库）
    async def handle_filter_data(self, websocket, data):
        selected_ids = data.get('selected_ids', [])
        
        self.log(f"开始处理数据筛选请求: 选中的ID数量={len(selected_ids)} from {websocket.remote_address}", 'INFO')
        
        if not selected_ids:
            self.log(f"筛选请求失败: 没有要筛选的数据 from {websocket.remote_address}", 'WARNING')
            response = C2SPackageHelper.error("没有要筛选的数据")
            await websocket.send(response)
            self.log(f"发送筛选失败响应: {response}", 'DEBUG')
            return
        
        # 根据选中的ID找到对应的搜索结果数据
        data_list = [result for result in self.last_search_results if result['id'] in selected_ids]
        
        self.log(f"根据选中的ID找到对应的数据: 数据数量={len(data_list)} from {websocket.remote_address}", 'INFO')
        
        if not data_list:
            self.log(f"筛选请求失败: 没有找到对应的筛选数据 from {websocket.remote_address}", 'WARNING')
            response = C2SPackageHelper.error("没有找到对应的筛选数据")
            await websocket.send(response)
            self.log(f"发送筛选失败响应: {response}", 'DEBUG')
            return
        
        # 发送筛选接收成功信号
        received_response = C2SPackageHelper.filter_received()
        await websocket.send(received_response)
        self.log(f"发送筛选接收成功响应: {received_response}", 'DEBUG')
        
        # 将选中的数据入库
        self.log(f"开始将数据入库: 数据数量={len(data_list)}", 'INFO')
        for item in data_list:
            try:
                self.db.add_data_record(
                    item.get('title', ''),
                    item.get('summary', ''),
                    item.get('image_url', ''),
                    item.get('source_url', ''),
                    item.get('data_source', '')
                )
                self.log(f"数据入库成功: 标题={item.get('title', '')}", 'DEBUG')
            except Exception as e:
                self.log(f"数据入库失败: 标题={item.get('title', '')} - 错误: {e}", 'ERROR')
        
        # 发送筛选完成信号
        completed_response = C2SPackageHelper.filter_completed()
        await websocket.send(completed_response)
        self.log(f"发送筛选完成响应: {completed_response}", 'DEBUG')
    
    # 处理数据管理页面刷新
    async def handle_refresh_data_management(self, websocket):
        # 发送正在读取信号
        await websocket.send(C2SPackageHelper.reading_data())
        
        # 读取数据库中的数据
        data_list = self.db.get_data_records()
        
        # 转换数据格式
        formatted_data = []
        for item in data_list:
            formatted_data.append({
                'id': item[0],
                'title': item[1],
                'summary': item[2],
                'image_url': item[3],
                'source_url': item[4],
                'data_source': item[5],
                'created_at': item[6]
            })
        
        # 发送数据读取完成信号和数据
        await websocket.send(C2SPackageHelper.data_read_completed(formatted_data))
    
    # 处理数据删除
    async def handle_delete_data(self, websocket, data):
        selected_ids = data.get('selected_ids', [])
        
        if not selected_ids:
            await websocket.send(C2SPackageHelper.error("没有要删除的数据"))
            return
        
        # 发送正在删除信号
        await websocket.send(C2SPackageHelper.deleting_data())
        
        # 删除选中的数据
        for record_id in selected_ids:
            self.db.delete_data_record(record_id)
        
        # 发送删除完成信号
        await websocket.send(C2SPackageHelper.data_deleted())
        
        # 重新读取数据库并发送数据
        await self.handle_refresh_data_management(websocket)
    
    # 处理搜索源管理页面刷新
    async def handle_refresh_search_source_management(self, websocket):
        # 发送正在寻找搜索源信号
        await websocket.send(C2SPackageHelper.finding_search_sources())
        
        # 获取所有搜索源
        all_sources = self.search_source_manager.get_all_sources()
        
        # 转换数据格式
        formatted_sources = []
        for source in all_sources:
            formatted_sources.append({
                'id': source['id'],
                'name': source['display_name'] if 'display_name' in source else source['name'],
                'description': source['description'] if 'description' in source else '',
                'is_active': source['enabled']
            })
        
        # 发送搜索源寻找完成信号和数据
        await websocket.send(C2SPackageHelper.search_sources_found(formatted_sources))
    
    # 处理搜索源禁用
    async def handle_disable_search_source(self, websocket, data):
        source_id = data.get('source_id')
        
        if not source_id:
            await websocket.send(C2SPackageHelper.error("没有指定要禁用的搜索源"))
            return
        
        # 发送正在禁用信号
        await websocket.send(C2SPackageHelper.disabling_search_source())
        
        # 将搜索源加入黑名单
        self.db.add_to_blacklist(source_id)
        
        # 重新加载搜索源
        self.search_source_manager = SearchSourceManager(self.db.get_blacklist())
        
        # 发送搜索源状态更新信号和数据
        all_sources = self.search_source_manager.get_all_sources()
        formatted_sources = []
        for source in all_sources:
            formatted_sources.append({
                'id': source['id'],
                'name': source['display_name'] if 'display_name' in source else source['name'],
                'description': source['description'] if 'description' in source else '',
                'is_active': source['enabled']
            })
        
        await websocket.send(C2SPackageHelper.search_source_status_updated(formatted_sources))
    
    # 处理搜索源启用
    async def handle_enable_search_source(self, websocket, data):
        source_id = data.get('source_id')
        
        if not source_id:
            await websocket.send(C2SPackageHelper.error("没有指定要启用的搜索源"))
            return
        
        # 发送正在禁用信号（复用同一个信号）
        await websocket.send(C2SPackageHelper.disabling_search_source())
        
        # 将搜索源从黑名单中移除
        self.db.remove_from_blacklist(source_id)
        
        # 重新加载搜索源
        self.search_source_manager = SearchSourceManager(self.db.get_blacklist())
        
        # 发送搜索源状态更新信号和数据
        all_sources = self.search_source_manager.get_all_sources()
        formatted_sources = []
        for source in all_sources:
            formatted_sources.append({
                'id': source['id'],
                'name': source['display_name'] if 'display_name' in source else source['name'],
                'description': source['description'] if 'description' in source else '',
                'is_active': source['enabled']
            })
        
        await websocket.send(C2SPackageHelper.search_source_status_updated(formatted_sources))
    
    async def start_server(self):
        """
        启动WebSocket服务器
        """
        try:
            server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port
            )
            
            self.log(f"WebSocket服务器已成功启动，地址: ws://{self.host}:{self.port}", 'INFO')
            
            await server.wait_closed()
        
        except Exception as e:
            self.log(f"WebSocket服务器启动失败: {str(e)}", 'CRITICAL')
            raise

if __name__ == "__main__":
    server = WebSocketServer()
    asyncio.run(server.start_server())