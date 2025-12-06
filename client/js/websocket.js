// WebSocket通信模块
const WebSocketClient = {
    socket: null,
    isConnected: false,
    callbacks: {},
    reconnectInterval: 5000, // 重连间隔时间（毫秒）
    reconnectTimer: null, // 重连定时器
    
    // 连接到WebSocket服务器
    connect: function(host = 'ws://localhost:8000') {
        console.log('客户端尝试连接WebSocket服务器:', host);
        try {
            this.socket = new WebSocket(host);
            
            this.socket.onopen = () => {
                console.log('客户端WebSocket连接已成功建立');
                this.isConnected = true;
                
                // 触发连接建立回调
                if (this.callbacks.onConnect) {
                    this.callbacks.onConnect();
                }
            };
            
            this.socket.onmessage = (event) => {
                console.log('客户端收到WebSocket消息:', event.data);
                try {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                } catch (error) {
                    console.error('客户端解析WebSocket消息失败:', error);
                }
            };
            
            this.socket.onerror = (error) => {
                console.error('客户端WebSocket连接错误:', error);
                
                // 触发错误回调
                if (this.callbacks.onError) {
                    this.callbacks.onError(error);
                }
            };
            
            this.socket.onclose = (event) => {
                console.log('客户端WebSocket连接已关闭:', event.code, event.reason);
                this.isConnected = false;
                
                // 触发连接关闭回调
                if (this.callbacks.onClose) {
                    this.callbacks.onClose(event);
                }
                
                // 启动自动重连
                this.startReconnect();
            };
        } catch (error) {
            console.error('客户端WebSocket连接尝试失败:', error);
            
            // 触发错误回调
            if (this.callbacks.onError) {
                this.callbacks.onError(error);
            }
        }
    },
    
    // 断开WebSocket连接
    disconnect: function() {
        if (this.socket) {
            this.socket.close();
        }
        
        // 清除重连定时器
        this.clearReconnect();
    },
    
    // 启动自动重连
    startReconnect: function() {
        this.clearReconnect();
        
        console.log('WebSocket将在' + this.reconnectInterval + '毫秒后尝试重连');
        this.reconnectTimer = setTimeout(() => {
            console.log('WebSocket尝试重连...');
            this.connect();
        }, this.reconnectInterval);
    },
    
    // 清除重连定时器
    clearReconnect: function() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
    },
    
    // 发送消息
    send: function(message) {
        console.log('客户端尝试发送WebSocket消息:', message);
        if (this.isConnected) {
            try {
                const jsonMessage = JSON.stringify(message);
                this.socket.send(jsonMessage);
                console.log('客户端WebSocket消息发送成功:', jsonMessage);
                return true;
            } catch (error) {
                console.error('客户端WebSocket消息发送失败:', error);
                return false;
            }
        } else {
            console.error('客户端WebSocket未连接，无法发送消息');
            return false;
        }
    },
    
    // 处理接收到的消息
    handleMessage: function(message) {
        console.log('客户端处理WebSocket消息:', message);
        
        // 根据消息类型触发相应的回调
        if (message.type && this.callbacks[message.type]) {
            console.log('客户端触发WebSocket消息回调:', message.type);
            this.callbacks[message.type](message.data);
        } else {
            console.warn('客户端未处理的WebSocket消息类型:', message.type);
        }
    },
    
    // 注册回调函数
    on: function(event, callback) {
        this.callbacks[event] = callback;
    },
    
    // 移除回调函数
    off: function(event) {
        delete this.callbacks[event];
    },
    
    // 发送网页嗅探请求
    sendSniffRequest: function(url, sourceId, sourceName) {
        const message = {
            type: 'sniff_webpage',
            data: {
                url: url,
                source_id: sourceId,
                source_name: sourceName
            }
        };
        this.send(message);
    },
    
    // 发送保存爬虫规则请求
    sendSaveCrawlerRuleRequest: function(ruleData) {
        const message = {
            type: 'save_crawler_rule',
            data: ruleData
        };
        this.send(message);
    },
    
    // 发送刷新爬虫规则请求
    sendRefreshCrawlerRulesRequest: function() {
        const message = {
            type: 'refresh_crawler_rules',
            data: {}
        };
        this.send(message);
    },
    
    // 发送启用爬虫规则请求
    sendEnableCrawlerRuleRequest: function(ruleId) {
        const message = {
            type: 'enable_crawler_rule',
            data: {
                id: ruleId
            }
        };
        this.send(message);
    },
    
    // 发送禁用爬虫规则请求
    sendDisableCrawlerRuleRequest: function(ruleId) {
        const message = {
            type: 'disable_crawler_rule',
            data: {
                id: ruleId
            }
        };
        this.send(message);
    },
    
    // 发送删除爬虫规则请求
    sendDeleteCrawlerRuleRequest: function(ruleId) {
        const message = {
            type: 'delete_crawler_rule',
            data: {
                id: ruleId
            }
        };
        this.send(message);
    }
};

// 导出WebSocketClient模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketClient;
}