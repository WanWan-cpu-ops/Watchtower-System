// WebSocket通信管理
class TelescopeWebSocket {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.url = 'ws://localhost:8765';
    }
    
    connect() {
        return new Promise((resolve, reject) => {
            try {
                console.log('正在连接WebSocket:', this.url);
                this.socket = new WebSocket(this.url);
                
                this.socket.onopen = () => {
                    console.log('WebSocket连接已建立');
                    this.isConnected = true;
                    
                    // 连接建立后自动刷新个人资料（如果在个人资料页面）
                    if (window.profilePage) {
                        window.profilePage.refreshVerificationStatus();
                    }
                    
                    resolve();
                };
                
                this.socket.onclose = () => {
                    console.log('WebSocket连接已关闭');
                    this.isConnected = false;
                };
                
                this.socket.onerror = (error) => {
                    console.error('WebSocket连接错误:', error);
                    reject(error);
                };
                
                this.socket.onmessage = (event) => {
                    this.handleMessage(event.data);
                };
            } catch (error) {
                console.error('WebSocket连接失败:', error);
                reject(error);
            }
        });
    }
    
    disconnect() {
        if (this.socket && this.isConnected) {
            this.socket.close();
            this.isConnected = false;
        }
    }
    
    /**
     * 发送数据包到服务器
     */
    send(data) {
        const message = JSON.stringify(data);
        console.log(`[${new Date().toLocaleTimeString()}] 发送数据包到服务器:`, message);
        if (this.socket && this.isConnected) {
            this.socket.send(message);
            console.log(`[${new Date().toLocaleTimeString()}] 数据发送成功`);
            return true;
        } else {
            console.error(`[${new Date().toLocaleTimeString()}] WebSocket未连接，无法发送数据`);
            return false;
        }
    }
    
    /**
     * 处理从服务器接收的消息
     */
    handleMessage(message) {
        try {
            console.log(`[${new Date().toLocaleTimeString()}] 收到服务器原始消息:`, message);
            const packet = JSON.parse(message);
            console.log(`[${new Date().toLocaleTimeString()}] 解析后的服务器消息:`, packet);
            
            switch (packet.msg_type) {
                case 'login':
                    this.handleLoginResponse(packet);
                    break;
                case 'register':
                    console.log('处理注册响应:', packet);
                    this.handleRegisterResponse(packet);
                    break;
                case 'search':
                    if (packet.status === 'processing') {
                        this.handleSearchProcessing(packet);
                    } else if (packet.status === 'completed') {
                        this.handleSearchResult(packet);
                    }
                    break;
                case 'filter':
                    if (packet.status === 'received') {
                        this.handleFilterAck(packet);
                    } else if (packet.status === 'completed') {
                        this.handleFilterComplete(packet);
                    }
                    break;
                case 'refresh_data':
                    this.handleDataRefreshResponse(packet);
                    break;
                case 'delete_data':
                    this.handleDataDeleteResponse(packet);
                    break;
                case 'refresh_sources':
                    this.handleSourceRefreshResponse(packet);
                    break;
                case 'toggle_source':
                    this.handleSourceStatusUpdate(packet);
                    break;
                case 'refresh_profile':
                    // 处理个人资料响应
                    break;
                case 'refresh_profile_response':
                    // 个人资料刷新响应
                    window.profilePage.handleProfileRefreshResponse(packet);
                    break;
                case 'send_verification_code_response':
                    // 验证码发送响应
                    window.profilePage.handleSmsResponse(packet);
                    break;
                case 'submit_verification_response':
                    // 实名认证提交响应
                    window.profilePage.handleVerificationResponse(packet);
                    break;
                default:
                    console.log('未知消息类型:', packet.msg_type);
            }
        } catch (error) {
            console.error('解析WebSocket消息失败:', error);
        }
    }
    
    handleLoginResponse(packet) {
        if (packet.status === 'success') {
            // 登录成功
            app.setCurrentUser(packet.data);
            app.showNavbar();
            app.switchPage('data-collection');
            app.hideLoading();
        } else {
            // 登录失败
            app.hideLoading();
            alert('登录失败: 用户名或密码错误');
        }
    }
    
    handleRegisterResponse(packet) {
        console.log('处理注册响应:', packet);
        try {
            // 首先隐藏加载指示器
            console.log('隐藏加载指示器');
            app.hideLoading();
            
            if (packet.status === 'success') {
                // 注册成功
                console.log('注册成功');
                alert('注册成功！请使用新账号登录');
                
                // 切换回登录页面
                console.log('检查window.loginPage:', window.loginPage);
                if (window.loginPage) {
                    console.log('调用showLoginPage方法');
                    window.loginPage.showLoginPage();
                } else {
                    console.error('window.loginPage未定义');
                    // 手动切换回登录页面
                    document.getElementById('login-page').classList.add('active');
                    document.getElementById('register-page').classList.remove('active');
                }
            } else {
                // 注册失败
                console.log('注册失败');
                alert('注册失败: ' + (packet.data?.message || '未知错误'));
            }
        } catch (error) {
            console.error('处理注册响应时出错:', error);
            // 确保加载指示器被隐藏
            app.hideLoading();
        }
    }
    
    handleSearchProcessing(packet) {
        // 显示正在搜索的提示
        app.showLoading('正在搜索...');
    }
    
    handleSearchResult(packet) {
        if (packet.status === 'completed') {
            // 搜索完成，更新搜索结果
            app.hideLoading();
            app.setSearchResults(packet.data.results);
            
            // 渲染搜索结果
            if (window.dataCollectionPage) {
                window.dataCollectionPage.renderSearchResults();
            }
        } else {
            // 搜索失败
            app.hideLoading();
            alert('搜索失败: ' + (packet.data?.message || '未知错误'));
        }
    }
    
    handleFilterAck(packet) {
        // 筛选接收成功
        app.showLoading('正在筛选数据...');
    }
    
    handleFilterComplete(packet) {
        // 筛选完成
        app.hideLoading();
        alert('数据筛选完成，已保存到数据库');
    }
    
    handleDataRefreshResponse(packet) {
        if (packet.status === 'success') {
            // 更新数据记录
            if (window.dataManagementPage) {
                window.dataManagementPage.renderDataRecords(packet.data.records);
            }
        } else {
            alert('刷新数据失败: ' + packet.data.message);
        }
    }
    
    handleSourceRefreshResponse(packet) {
        if (packet.status === 'success') {
            // 更新搜索源列表
            if (window.sourceManagementPage) {
                window.sourceManagementPage.renderSourceList(packet.data.sources);
            }
        } else {
            alert('刷新搜索源失败: ' + packet.data.message);
        }
    }
    
    handleSourceStatusUpdate(packet) {
        if (packet.status === 'success') {
            // 更新搜索源状态
            if (window.sourceManagementPage) {
                window.sourceManagementPage.renderSourceList(packet.data.sources);
            }
        } else {
            alert('更新搜索源状态失败: ' + packet.data.message);
        }
    }
    
    handleDataDeleteResponse(packet) {
        if (packet.status === 'success') {
            // 更新数据记录
            if (window.dataManagementPage) {
                window.dataManagementPage.renderDataRecords(packet.data.records);
            }
        } else {
            alert('删除数据失败: ' + packet.data.message);
        }
    }
    
    handleError(packet) {
        app.hideLoading();
        alert('操作失败: ' + packet.data.message);
    }
}

// 初始化WebSocket
const ws = new TelescopeWebSocket();

// 当DOM加载完成后，尝试连接WebSocket
document.addEventListener('DOMContentLoaded', () => {
    ws.connect().catch(error => {
        console.log('初始WebSocket连接失败，将在登录时重试:', error);
    });
});