// 登录页面逻辑
class LoginPage {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // 登录按钮点击事件
        document.getElementById('login-btn').addEventListener('click', () => {
            this.login();
        });
        
        // 回车键登录
        document.getElementById('username').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.login();
            }
        });
        
        document.getElementById('password').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.login();
            }
        });
        
        // 注册页面切换
        document.getElementById('show-register-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.showRegisterPage();
        });
        
        document.getElementById('show-login-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.showLoginPage();
        });
        
        // 注册按钮点击事件
        document.getElementById('register-btn').addEventListener('click', () => {
            this.register();
        });
        
        // 回车键注册
        document.getElementById('register-username').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.register();
            }
        });
        
        document.getElementById('register-password').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.register();
            }
        });
        
        document.getElementById('confirm-password').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.register();
            }
        });
    }
    
    showLoginPage() {
        document.getElementById('login-page').classList.add('active');
        document.getElementById('register-page').classList.remove('active');
    }
    
    showRegisterPage() {
        document.getElementById('register-page').classList.add('active');
        document.getElementById('login-page').classList.remove('active');
    }
    
    login() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        
        if (!username || !password) {
            alert('请输入用户名和密码');
            return;
        }
        
        // 显示加载指示器
        app.showLoading('正在登录...');
        
        // 检查WebSocket连接状态，如果未连接则尝试连接
        if (!ws.isConnected) {
            ws.connect()
                .then(() => {
                    this.sendLoginRequest(username, password);
                })
                .catch(error => {
                    console.error('WebSocket连接失败:', error);
                    app.hideLoading();
                    alert('无法连接到服务器，请稍后重试');
                });
        } else {
            this.sendLoginRequest(username, password);
        }
    }
    
    sendLoginRequest(username, password) {
        // 发送登录请求
        const loginPacket = {
            msg_type: 'login',
            data: {
                username: username,
                password: password
            }
        };
        
        ws.send(loginPacket);
    }
    
    register() {
        const username = document.getElementById('register-username').value.trim();
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        
        if (!username || !password || !confirmPassword) {
            alert('请输入所有必填字段');
            return;
        }
        
        if (password !== confirmPassword) {
            alert('两次输入的密码不一致');
            return;
        }
        
        // 显示加载指示器
        app.showLoading('正在注册...');
        
        // 检查WebSocket连接状态，如果未连接则尝试连接
        if (!ws.isConnected) {
            ws.connect()
                .then(() => {
                    this.sendRegisterRequest(username, password);
                })
                .catch(error => {
                    console.error('WebSocket连接失败:', error);
                    app.hideLoading();
                    alert('无法连接到服务器，请稍后重试');
                });
        } else {
            this.sendRegisterRequest(username, password);
        }
    }
    
    sendRegisterRequest(username, password) {
        // 发送注册请求
        const registerPacket = {
            msg_type: 'register',
            data: {
                username: username,
                password: password
            }
        };
        
        console.log('发送注册请求:', registerPacket);
        const success = ws.send(registerPacket);
        console.log('注册请求发送结果:', success);
    }
}

// 初始化登录页面
const loginPage = new LoginPage();

// 将loginPage添加到全局作用域，以便在其他文件中访问
window.loginPage = loginPage;