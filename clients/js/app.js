// 主应用文件
class TelescopeApp {
    constructor() {
        this.currentUser = null;
        this.currentPage = 'login';
        this.websocket = null;
        this.searchResults = [];
        this.currentPageResults = 1;
        this.resultsPerPage = 18; // 6行 * 3列
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.hideNavbar();
    }
    
    setupEventListeners() {
        // 导航栏页面切换
        document.querySelectorAll('.nav-link[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.getAttribute('data-page');
                this.switchPage(page);
            });
        });
        
        // 退出登录
        document.getElementById('logout-btn').addEventListener('click', () => {
            this.logout();
        });
    }
    
    switchPage(pageName) {
        // 隐藏所有页面
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        
        // 显示目标页面
        const targetPage = document.getElementById(pageName);
        if (targetPage) {
            targetPage.classList.add('active');
            this.currentPage = pageName;
            
            // 根据页面名称更新导航栏链接的激活状态
            document.querySelectorAll('.nav-link[data-page]').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('data-page') === pageName) {
                    link.classList.add('active');
                }
            });
            
            // 页面切换时的特殊处理
            this.handlePageSwitch(pageName);
        }
    }
    
    handlePageSwitch(pageName) {
        switch(pageName) {
            case 'data-collection':
                // 可以在这里添加数据采集页面的初始化代码
                break;
            case 'data-management':
                // 发送数据管理页面刷新请求
                if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                    const refreshPacket = {
                        type: 'data_refresh',
                        data: {}
                    };
                    this.websocket.send(JSON.stringify(refreshPacket));
                }
                break;
            case 'source-management':
                // 发送搜索源管理页面刷新请求
                if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                    const refreshPacket = {
                        type: 'source_refresh',
                        data: {}
                    };
                    this.websocket.send(JSON.stringify(refreshPacket));
                }
                break;
            case 'profile':
                // 更新个人资料页面
                if (this.currentUser) {
                    document.getElementById('profile-username').textContent = this.currentUser.username;
                    document.getElementById('profile-permission').textContent = this.currentUser.permission_level;
                }
                // 尝试刷新实名认证状态
                if (window.profilePage) {
                    window.profilePage.refreshVerificationStatus();
                }
                break;
        }
    }
    
    showNavbar() {
        document.getElementById('navbar').style.display = 'block';
    }
    
    hideNavbar() {
        document.getElementById('navbar').style.display = 'none';
    }
    
    showLoading(message = '处理中...') {
        const loadingIndicator = document.getElementById('loading-indicator');
        const loadingMessage = document.getElementById('loading-message');
        loadingMessage.textContent = message;
        loadingIndicator.classList.add('show');
    }
    
    hideLoading() {
        const loadingIndicator = document.getElementById('loading-indicator');
        loadingIndicator.classList.remove('show');
    }
    
    // Toast通知功能
    showToast(message, type = 'info', duration = 3000) {
        const toastContainer = document.getElementById('toast-container');
        const toastId = `toast-${Date.now()}`;
        
        const toast = document.createElement('div');
        toast.className = `toast fade show ${type}`;
        toast.id = toastId;
        toast.innerHTML = `
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // 自动关闭
        setTimeout(() => {
            this.hideToast(toastId);
        }, duration);
        
        return toastId;
    }
    
    hideToast(toastId) {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.classList.remove('show');
            toast.classList.add('hide');
            setTimeout(() => {
                toast.remove();
            }, 500);
        }
    }
    
    // 本地存储管理
    setLocalStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('保存到本地存储失败:', error);
        }
    }
    
    getLocalStorage(key) {
        try {
            const value = localStorage.getItem(key);
            return value ? JSON.parse(value) : null;
        } catch (error) {
            console.error('从本地存储获取失败:', error);
            return null;
        }
    }
    
    removeLocalStorage(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('从本地存储删除失败:', error);
        }
    }
    
    login(username, password) {
        // 登录逻辑由login.js处理
    }
    
    logout() {
        // 关闭WebSocket连接
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        // 清除用户信息
        this.currentUser = null;
        
        // 切换到登录页
        this.switchPage('login');
        this.hideNavbar();
        
        // 清除本地存储
        localStorage.removeItem('telescope_user');
    }
    
    setCurrentUser(user) {
        this.currentUser = user;
        localStorage.setItem('telescope_user', JSON.stringify(user));
    }
    
    getCurrentUser() {
        if (!this.currentUser) {
            const storedUser = localStorage.getItem('telescope_user');
            if (storedUser) {
                this.currentUser = JSON.parse(storedUser);
            }
        }
        return this.currentUser;
    }
    
    setWebSocket(ws) {
        this.websocket = ws;
    }
    
    // 分页相关方法
    setSearchResults(results) {
        this.searchResults = results;
        this.currentPageResults = 1;
        this.renderPagination();
    }
    
    getCurrentPageResults() {
        const startIndex = (this.currentPageResults - 1) * this.resultsPerPage;
        const endIndex = startIndex + this.resultsPerPage;
        return this.searchResults.slice(startIndex, endIndex);
    }
    
    nextPageResults() {
        if (this.currentPageResults < this.getTotalPages()) {
            this.currentPageResults++;
            this.renderPagination();
            return true;
        }
        return false;
    }
    
    prevPageResults() {
        if (this.currentPageResults > 1) {
            this.currentPageResults--;
            this.renderPagination();
            return true;
        }
        return false;
    }
    
    goToPageResults(page) {
        if (page >= 1 && page <= this.getTotalPages()) {
            this.currentPageResults = page;
            this.renderPagination();
            return true;
        }
        return false;
    }
    
    getTotalPages() {
        return Math.ceil(this.searchResults.length / this.resultsPerPage);
    }
    
    renderPagination() {
        const paginationContainer = document.getElementById('pagination');
        if (!paginationContainer) return;
        
        const totalPages = this.getTotalPages();
        if (totalPages <= 1) {
            paginationContainer.innerHTML = '';
            return;
        }
        
        let paginationHTML = '<div class="pagination">';
        
        // 上一页按钮
        paginationHTML += `<button id="prev-page" ${this.currentPageResults === 1 ? 'disabled' : ''}>上一页</button>`;
        
        // 页码按钮
        for (let i = 1; i <= totalPages; i++) {
            paginationHTML += `<button class="page-btn ${i === this.currentPageResults ? 'active' : ''}" data-page="${i}">${i}</button>`;
        }
        
        // 下一页按钮
        paginationHTML += `<button id="next-page" ${this.currentPageResults === totalPages ? 'disabled' : ''}>下一页</button>`;
        
        paginationHTML += '</div>';
        
        paginationContainer.innerHTML = paginationHTML;
        
        // 添加事件监听器
        document.getElementById('prev-page').addEventListener('click', () => {
            if (this.prevPageResults()) {
                this.renderSearchResults();
            }
        });
        
        document.getElementById('next-page').addEventListener('click', () => {
            if (this.nextPageResults()) {
                this.renderSearchResults();
            }
        });
        
        document.querySelectorAll('.page-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const page = parseInt(e.target.getAttribute('data-page'));
                if (this.goToPageResults(page)) {
                    this.renderSearchResults();
                }
            });
        });
    }
    
    renderSearchResults() {
        // 由data-collection.js实现
    }
}

// 初始化应用
const app = new TelescopeApp();