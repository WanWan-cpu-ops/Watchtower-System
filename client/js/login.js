// 登录页面的JavaScript文件

// 页面加载完成后执行
window.addEventListener('load', function() {
    // 获取DOM元素
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginMessage = document.getElementById('login-message');
    
    // 连接到WebSocket服务器
    WebSocketClient.connect();
    
    // 注册连接建立回调
    WebSocketClient.on('onConnect', function() {
        console.log('WebSocket连接已建立，可以进行登录操作');
    });
    
    // 注册登录响应回调
    WebSocketClient.on('login_response', function(data) {
        if (data.status === 'success') {
            // 登录成功，保存用户信息并跳转到主页面
            sessionStorage.setItem('user', JSON.stringify(data.user));
            loginMessage.textContent = '登录成功，正在跳转到主页面...';
            loginMessage.style.backgroundColor = 'rgba(76, 175, 80, 0.3)';
            loginMessage.style.color = '#4caf50';
            
            // 延迟1秒后跳转到主页面
            setTimeout(function() {
                window.location.href = 'index.html';
            }, 1000);
        } else {
            // 登录失败，显示错误消息
            loginMessage.textContent = '登录失败：' + data.message;
            loginMessage.style.backgroundColor = 'rgba(244, 67, 54, 0.3)';
            loginMessage.style.color = '#f44336';
        }
    });
    
    // 注册WebSocket错误回调
    WebSocketClient.on('onError', function(error) {
        loginMessage.textContent = '连接服务器失败：' + error.message;
        loginMessage.style.backgroundColor = 'rgba(244, 67, 54, 0.3)';
        loginMessage.style.color = '#f44336';
    });
    
    // 登录表单提交事件处理
    loginForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // 获取用户名和密码
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();
        
        // 验证输入
        if (!username || !password) {
            loginMessage.textContent = '请输入用户名和密码';
            loginMessage.style.backgroundColor = 'rgba(255, 193, 7, 0.3)';
            loginMessage.style.color = '#ffc107';
            return;
        }
        
        // 发送登录请求
        const loginRequest = {
            type: 'login',
            data: {
                username: username,
                password: password
            }
        };
        
        if (WebSocketClient.send(loginRequest)) {
            loginMessage.textContent = '正在登录...';
            loginMessage.style.backgroundColor = 'rgba(33, 150, 243, 0.3)';
            loginMessage.style.color = '#2196f3';
        } else {
            loginMessage.textContent = '发送登录请求失败，请检查连接';
            loginMessage.style.backgroundColor = 'rgba(244, 67, 54, 0.3)';
            loginMessage.style.color = '#f44336';
        }
    });
});

// 页面卸载时断开WebSocket连接
window.addEventListener('beforeunload', function() {
    WebSocketClient.disconnect();
});