// 主应用页面的JavaScript文件

// 应用状态
const AppState = {
    currentUser: null,
    searchResults: [],
    currentPage: 1,
    itemsPerPage: 18, // 6行 × 3列
    selectedItems: new Set(),
    dataRecords: [],
    searchSources: [],
    crawlerRules: [],
    sniffingInProgress: false,
    sniffingResult: null
};

// 页面加载完成后执行
window.addEventListener('load', function() {
    // 检查用户是否已登录
    const userData = sessionStorage.getItem('user');
    if (!userData) {
        // 用户未登录，跳转到登录页面
        window.location.href = 'login.html';
        return;
    }
    
    // 解析用户数据
    AppState.currentUser = JSON.parse(userData);
    
    // 初始化应用
    initializeApp();
});

// 初始化应用
function initializeApp() {
    // 连接到WebSocket服务器
    WebSocketClient.connect();
    
    // 注册WebSocket事件回调
    registerWebSocketCallbacks();
    
    // 初始化页面元素
    initializePageElements();
    
    // 加载个人资料
    loadProfile();
    
    // 注册连接建立回调，在连接建立后刷新数据
    WebSocketClient.on('onConnect', function() {
        // 刷新数据管理页面
        refreshDataManagementPage();
        
        // 刷新搜索源管理页面
        refreshSearchSourceManagementPage();
        
        // 刷新爬虫规则管理页面
        refreshCrawlerRuleManagementPage();
    });
}

// 注册WebSocket事件回调
function registerWebSocketCallbacks() {
    // 连接建立回调
    WebSocketClient.on('onConnect', function() {
        console.log('WebSocket连接已建立');
    });
    
    // 连接关闭回调
    WebSocketClient.on('onClose', function() {
        console.log('WebSocket连接已关闭');
    });
    
    // 错误回调
    WebSocketClient.on('onError', function(error) {
        console.error('WebSocket错误:', error);
        showStatusMessage('连接服务器失败：' + error.message, 'error');
    });
    
    // 处理服务端发送的错误响应
    WebSocketClient.on('error', function(data) {
        console.error('客户端处理WebSocket错误响应:', data);
        showStatusMessage(data.message, 'error');
    });
    
    // 处理网页嗅探响应
    WebSocketClient.on('sniffing', function(data) {
        if (data.status === 'sniffing') {
            showStatusMessage('正在嗅探网页内容...', 'info');
            AppState.sniffingInProgress = true;
            document.getElementById('start-sniff-button').disabled = true;
        } else if (data.status === 'completed') {
            showStatusMessage('网页嗅探完成', 'success');
            AppState.sniffingInProgress = false;
            AppState.sniffingResult = data.result;
            document.getElementById('start-sniff-button').disabled = false;
            displaySniffingResult();
        } else if (data.status === 'failed') {
            showStatusMessage('网页嗅探失败：' + data.message, 'error');
            AppState.sniffingInProgress = false;
            document.getElementById('start-sniff-button').disabled = false;
        }
    });
    
    // 处理保存爬虫规则响应
    WebSocketClient.on('crawler_rule_saved', function(data) {
        if (data.success) {
            showStatusMessage('爬虫规则保存成功', 'success');
            // 清空嗅探结果
            AppState.sniffingResult = null;
            document.getElementById('sniff-url-input').value = '';
            document.getElementById('source-id-input').value = '';
            document.getElementById('source-name-input').value = '';
            document.getElementById('sniffing-result').innerHTML = '';
            // 刷新规则列表
            refreshCrawlerRuleManagementPage();
        } else {
            showStatusMessage('爬虫规则保存失败：' + data.message, 'error');
        }
    });
    
    // 处理爬虫规则读取响应
    WebSocketClient.on('crawler_rules_read_completed', function(data) {
        if (data.success) {
            AppState.crawlerRules = data.rules;
            displayCrawlerRules();
        } else {
            showStatusMessage('读取爬虫规则失败：' + data.message, 'error');
        }
    });
    
    // 数据搜索响应回调
    WebSocketClient.on('search_response', function(data) {
        if (data.status === 'searching') {
            showStatusMessage('正在搜索数据...', 'info');
        } else if (data.status === 'completed') {
            AppState.searchResults = data.results;
            AppState.currentPage = 1;
            displaySearchResults();
            showStatusMessage('搜索完成，共找到 ' + AppState.searchResults.length + ' 条数据', 'success');
        } else if (data.status === 'failed') {
            showStatusMessage('搜索失败：' + data.message, 'error');
        }
    });
    
    // 数据筛选响应回调
    WebSocketClient.on('filter_response', function(data) {
        if (data.status === 'received') {
            showStatusMessage('正在筛选数据...', 'info');
        } else if (data.status === 'completed') {
            showStatusMessage('数据筛选完成，已成功入库 ' + data.count + ' 条数据', 'success');
            
            // 清空选择的项目
            AppState.selectedItems.clear();
            
            // 刷新数据管理页面
            refreshDataManagementPage();
        } else if (data.status === 'failed') {
            showStatusMessage('数据筛选失败：' + data.message, 'error');
        }
    });
    
    // 数据管理响应回调
    WebSocketClient.on('data_management_response', function(data) {
        if (data.status === 'reading') {
            showStatusMessage('正在读取数据...', 'info');
        } else if (data.status === 'completed') {
            AppState.dataRecords = data.records;
            displayDataRecords();
            showStatusMessage('数据读取完成，共 ' + AppState.dataRecords.length + ' 条数据', 'success');
        } else if (data.status === 'deleting') {
            showStatusMessage('正在删除数据...', 'info');
        } else if (data.status === 'delete_completed') {
            showStatusMessage('数据删除完成', 'success');
            
            // 清空选择的项目
            AppState.selectedItems.clear();
        } else if (data.status === 'failed') {
            showStatusMessage('数据管理操作失败：' + data.message, 'error');
        }
    });
    
    // 搜索源管理响应回调
    WebSocketClient.on('search_source_response', function(data) {
        if (data.status === 'searching') {
            showStatusMessage('正在寻找搜索源...', 'info');
        } else if (data.status === 'completed') {
            AppState.searchSources = data.sources;
            displaySearchSources();
            showStatusMessage('搜索源读取完成，共 ' + AppState.searchSources.length + ' 个搜索源', 'success');
        } else if (data.status === 'updating') {
            showStatusMessage('正在更新搜索源状态...', 'info');
        } else if (data.status === 'update_completed') {
            AppState.searchSources = data.sources;
            displaySearchSources();
            showStatusMessage('搜索源状态更新完成', 'success');
        } else if (data.status === 'failed') {
            showStatusMessage('搜索源管理操作失败：' + data.message, 'error');
        }
    });
    
    // 处理读取数据中消息
    WebSocketClient.on('reading_data', function(data) {
        console.log('客户端收到读取数据中消息:', data);
        showStatusMessage('正在读取数据...', 'info');
    });
    
    // 处理数据读取完成消息
    WebSocketClient.on('data_read_completed', function(data) {
        console.log('客户端收到数据读取完成消息:', data);
        AppState.dataRecords = data.data_list;
        displayDataRecords();
        showStatusMessage('数据读取完成，共 ' + AppState.dataRecords.length + ' 条数据', 'success');
    });
    
    // 处理寻找搜索源消息
    WebSocketClient.on('finding_search_sources', function(data) {
        console.log('客户端收到寻找搜索源消息:', data);
        showStatusMessage('正在寻找搜索源...', 'info');
    });
    
    // 处理搜索源找到消息
    WebSocketClient.on('search_sources_found', function(data) {
        console.log('客户端收到搜索源找到消息:', data);
        AppState.searchSources = data.source_list;
        displaySearchSources();
        showStatusMessage('搜索源读取完成，共 ' + AppState.searchSources.length + ' 个搜索源', 'success');
    });
    
    // 处理搜索源状态更新消息
    WebSocketClient.on('search_source_status_updated', function(data) {
        console.log('客户端收到搜索源状态更新消息:', data);
        AppState.searchSources = data.source_list;
        displaySearchSources();
        showStatusMessage('搜索源状态已更新', 'success');
    });
    
    // 处理搜索中消息
    WebSocketClient.on('searching', function(data) {
        console.log('客户端收到搜索中消息:', data);
        showStatusMessage('正在搜索数据...', 'info');
    });
    
    // 处理搜索完成消息
    WebSocketClient.on('search_completed', function(data) {
        console.log('客户端收到搜索完成消息:', data);
        AppState.searchResults = data.data_list;
        AppState.currentPage = 1;
        displaySearchResults();
        showStatusMessage('搜索完成，共找到 ' + AppState.searchResults.length + ' 条数据', 'success');
    });
}

// 初始化页面元素
function initializePageElements() {
    // 初始化导航栏
    initializeNavigation();
    
    // 初始化数据采集页面元素
    initializeDataCollectionPage();
    
    // 初始化数据管理页面元素
    initializeDataManagementPage();
    
    // 初始化搜索源管理页面元素
    initializeSearchSourceManagementPage();
    
    // 初始化个人资料页面元素
    initializeProfilePage();
    
    // 初始化爬虫规则管理页面元素
    initializeCrawlerRuleManagementPage();
    
    // 初始化模态框
    initializeModal();
}

// 初始化导航栏
function initializeNavigation() {
    const navbarItems = document.querySelectorAll('.navbar-item');
    
    navbarItems.forEach(item => {
        item.addEventListener('click', function(event) {
            event.preventDefault();
            
            // 移除所有导航项的active类
            navbarItems.forEach(i => i.classList.remove('active'));
            
            // 添加当前导航项的active类
            this.classList.add('active');
            
            // 获取目标页面ID
            const targetPageId = this.getAttribute('href').substring(1);
            
            // 切换到目标页面
            switchPage(targetPageId);
        });
    });
}

// 切换页面
function switchPage(pageId) {
    const pages = document.querySelectorAll('.page');
    
    pages.forEach(page => {
        page.classList.remove('active');
    });
    
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.add('active');
        
        // 切换到数据管理页面时触发刷新
        if (pageId === 'data-management') {
            refreshDataManagementPage();
        }
        
        // 切换到搜索源管理页面时触发刷新
        if (pageId === 'search-source-management') {
            refreshSearchSourceManagementPage();
        }
    }
}

// 初始化数据采集页面元素
function initializeDataCollectionPage() {
    // 获取DOM元素
    const startSearchBtn = document.getElementById('start-search');
    const searchContentInput = document.getElementById('search-content');
    const maxPagesInput = document.getElementById('max-pages');
    const selectAllBtn = document.getElementById('select-all');
    const deselectAllBtn = document.getElementById('deselect-all');
    const filterSelectedBtn = document.getElementById('filter-selected');
    
    // 开始搜索按钮点击事件
    startSearchBtn.addEventListener('click', function() {
        const searchContent = searchContentInput.value.trim();
        const maxPages = parseInt(maxPagesInput.value) || 1;
        
        if (!searchContent) {
            showStatusMessage('请输入搜索内容', 'warning');
            return;
        }
        
        // 发送数据搜索请求
        const searchRequest = {
            type: 'search_data',
            data: {
                search_content: searchContent,
                max_pages: maxPages
            }
        };
        
        if (WebSocketClient.send(searchRequest)) {
            // 清空之前的搜索结果
            AppState.searchResults = [];
            AppState.selectedItems.clear();
            document.getElementById('search-results').innerHTML = '';
            document.getElementById('pagination').innerHTML = '';
        } else {
            showStatusMessage('发送搜索请求失败，请检查连接', 'error');
        }
    });
    
    // 全选按钮点击事件
    selectAllBtn.addEventListener('click', function() {
        const currentPageResults = getCurrentPageResults();
        
        currentPageResults.forEach(result => {
            AppState.selectedItems.add(result.id);
        });
        
        updateDataCardSelections();
    });
    
    // 取消全选按钮点击事件
    deselectAllBtn.addEventListener('click', function() {
        const currentPageResults = getCurrentPageResults();
        
        currentPageResults.forEach(result => {
            AppState.selectedItems.delete(result.id);
        });
        
        updateDataCardSelections();
    });
    
    // 筛选选中数据按钮点击事件
    filterSelectedBtn.addEventListener('click', function() {
        if (AppState.selectedItems.size === 0) {
            showStatusMessage('请先选择要筛选的数据', 'warning');
            return;
        }
        
        // 发送数据筛选请求
        const filterRequest = {
            type: 'filter_data',
            data: {
                selected_ids: Array.from(AppState.selectedItems)
            }
        };
        
        if (WebSocketClient.send(filterRequest)) {
            // 清空搜索结果显示
            document.getElementById('search-results').innerHTML = '';
            document.getElementById('pagination').innerHTML = '';
        } else {
            showStatusMessage('发送筛选请求失败，请检查连接', 'error');
        }
    });
}

// 初始化数据管理页面元素
function initializeDataManagementPage() {
    // 获取DOM元素
    const searchDataBtn = document.getElementById('search-data');
    const dataSearchContentInput = document.getElementById('data-search-content');
    const dataSearchFieldSelect = document.getElementById('data-search-field');
    const selectAllDataBtn = document.getElementById('select-all-data');
    const deselectAllDataBtn = document.getElementById('deselect-all-data');
    const deleteSelectedDataBtn = document.getElementById('delete-selected-data');
    const analyzeSelectedDataBtn = document.getElementById('analyze-selected-data');
    
    // 搜索数据按钮点击事件
    searchDataBtn.addEventListener('click', function() {
        const searchContent = dataSearchContentInput.value.trim();
        const searchField = dataSearchFieldSelect.value;
        
        if (!searchContent) {
            // 没有搜索内容，刷新所有数据
            refreshDataManagementPage();
            return;
        }
        
        // 这里可以添加数据搜索逻辑
        // 目前先简单过滤本地数据
        const filteredRecords = AppState.dataRecords.filter(record => {
            return record[searchField].toLowerCase().includes(searchContent.toLowerCase());
        });
        
        AppState.dataRecords = filteredRecords;
        displayDataRecords();
        showStatusMessage('搜索完成，共找到 ' + filteredRecords.length + ' 条数据', 'success');
    });
    
    // 全选按钮点击事件
    selectAllDataBtn.addEventListener('click', function() {
        AppState.dataRecords.forEach(record => {
            AppState.selectedItems.add(record.id);
        });
        
        updateDataItemSelections();
    });
    
    // 取消全选按钮点击事件
    deselectAllDataBtn.addEventListener('click', function() {
        AppState.dataRecords.forEach(record => {
            AppState.selectedItems.delete(record.id);
        });
        
        updateDataItemSelections();
    });
    
    // 删除选中数据按钮点击事件
    deleteSelectedDataBtn.addEventListener('click', function() {
        if (AppState.selectedItems.size === 0) {
            showStatusMessage('请先选择要删除的数据', 'warning');
            return;
        }
        
        // 检查用户权限
        if (AppState.currentUser.permission_level < 2) {
            showStatusMessage('您的权限不足，无法删除数据', 'error');
            return;
        }
        
        // 确认删除
        if (confirm('确定要删除选中的 ' + AppState.selectedItems.size + ' 条数据吗？')) {
            // 发送数据删除请求
            const deleteRequest = {
                type: 'delete_data',
                data: {
                    selected_ids: Array.from(AppState.selectedItems)
                }
            };
            
            if (!WebSocketClient.send(deleteRequest)) {
                showStatusMessage('发送删除请求失败，请检查连接', 'error');
            }
        }
    });
    
    // 分析选中数据按钮点击事件
    analyzeSelectedDataBtn.addEventListener('click', function() {
        if (AppState.selectedItems.size === 0) {
            showStatusMessage('请先选择要分析的数据', 'warning');
            return;
        }
        
        // 这里可以添加数据分析逻辑
        showStatusMessage('数据分析功能将在后续版本中实现', 'info');
    });
}

// 初始化搜索源管理页面元素
function initializeSearchSourceManagementPage() {
    // 获取刷新按钮元素
    const refreshSearchSourcesBtn = document.getElementById('refresh-search-sources');
    
    // 刷新按钮点击事件
    refreshSearchSourcesBtn.addEventListener('click', function() {
        refreshSearchSourceManagementPage();
    });
}

// 初始化个人资料页面元素
function initializeProfilePage() {
    // 获取DOM元素
    const logoutBtn = document.getElementById('logout');
    
    // 退出登录按钮点击事件
    logoutBtn.addEventListener('click', function() {
        if (confirm('确定要退出登录吗？')) {
            // 清空会话存储的用户信息
            sessionStorage.removeItem('user');
            
            // 断开WebSocket连接
            WebSocketClient.disconnect();
            
            // 跳转到登录页面
            window.location.href = 'login.html';
        }
    });
}

// 初始化爬虫规则管理页面
function initializeCrawlerRuleManagementPage() {
    // 获取页面元素
    const startSniffButton = document.getElementById('start-sniff-button');
    const saveRuleButton = document.getElementById('save-rule-button');
    const refreshRulesButton = document.getElementById('refresh-rules-button');
    
    // 添加事件监听
    if (startSniffButton) {
        startSniffButton.addEventListener('click', handleStartSniffing);
    }
    
    if (saveRuleButton) {
        saveRuleButton.addEventListener('click', handleSaveRule);
    }
    
    if (refreshRulesButton) {
        refreshRulesButton.addEventListener('click', refreshCrawlerRuleManagementPage);
    }
}

// 处理开始嗅探按钮点击
function handleStartSniffing() {
    const urlInput = document.getElementById('sniff-url-input');
    const sourceIdInput = document.getElementById('source-id-input');
    const sourceNameInput = document.getElementById('source-name-input');
    
    const url = urlInput.value.trim();
    const sourceId = sourceIdInput.value.trim();
    const sourceName = sourceNameInput.value.trim();
    
    if (!url) {
        showStatusMessage('请输入要嗅探的网页URL', 'warning');
        return;
    }
    
    if (!sourceId) {
        showStatusMessage('请输入源ID', 'warning');
        return;
    }
    
    if (!sourceName) {
        showStatusMessage('请输入源名称', 'warning');
        return;
    }
    
    // 发送嗅探请求
    WebSocketClient.sendSniffRequest(url, sourceId, sourceName);
}

// 处理保存规则按钮点击
function handleSaveRule() {
    if (!AppState.sniffingResult) {
        showStatusMessage('请先完成网页嗅探', 'warning');
        return;
    }
    
    const urlInput = document.getElementById('sniff-url-input');
    const sourceIdInput = document.getElementById('source-id-input');
    const sourceNameInput = document.getElementById('source-name-input');
    
    const url = urlInput.value.trim();
    const sourceId = sourceIdInput.value.trim();
    const sourceName = sourceNameInput.value.trim();
    
    // 发送保存规则请求
    WebSocketClient.sendSaveCrawlerRuleRequest({
        source_id: sourceId,
        source_name: sourceName,
        url: url,
        title_xpath: AppState.sniffingResult.title_xpath,
        content_xpath: AppState.sniffingResult.content_xpath,
        image_xpath: AppState.sniffingResult.image_xpath,
        url_xpath: AppState.sniffingResult.url_xpath,
        request_headers: AppState.sniffingResult.request_headers
    });
}

// 刷新爬虫规则管理页面
function refreshCrawlerRuleManagementPage() {
    WebSocketClient.sendRefreshCrawlerRulesRequest();
}

// 显示嗅探结果
function displaySniffingResult() {
    const resultElement = document.getElementById('sniffing-result');
    if (!resultElement || !AppState.sniffingResult) {
        return;
    }
    
    const result = AppState.sniffingResult;
    let html = `
        <h3>嗅探结果</h3>
        <div class="sniffing-result-section">
            <h4>标题 XPath:</h4>
            <code>${result.title_xpath || '未找到'}</code>
        </div>
        <div class="sniffing-result-section">
            <h4>内容 XPath:</h4>
            <code>${result.content_xpath || '未找到'}</code>
        </div>
        <div class="sniffing-result-section">
            <h4>图片 XPath:</h4>
            <code>${result.image_xpath || '未找到'}</code>
        </div>
        <div class="sniffing-result-section">
            <h4>链接 XPath:</h4>
            <code>${result.url_xpath || '未找到'}</code>
        </div>
        <div class="sniffing-result-section">
            <h4>请求头:</h4>
            <pre>${JSON.stringify(result.request_headers, null, 2)}</pre>
        </div>
    `;
    
    resultElement.innerHTML = html;
    
    // 显示保存规则按钮
    document.getElementById('save-rule-button').style.display = 'block';
}

// 显示爬虫规则列表
function displayCrawlerRules() {
    const rulesListElement = document.getElementById('crawler-rules-list');
    if (!rulesListElement) {
        return;
    }
    
    if (AppState.crawlerRules.length === 0) {
        rulesListElement.innerHTML = '<p>暂无爬虫规则</p>';
        return;
    }
    
    let html = `
        <table class="rules-table">
            <thead>
                <tr>
                    <th>源ID</th>
                    <th>源名称</th>
                    <th>标题XPath</th>
                    <th>内容XPath</th>
                    <th>状态</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    AppState.crawlerRules.forEach(rule => {
        const statusClass = rule.is_enabled ? 'status-active' : 'status-inactive';
        const statusText = rule.is_enabled ? '启用' : '禁用';
        
        html += `
            <tr>
                <td>${rule.source_id}</td>
                <td>${rule.source_name}</td>
                <td><code>${rule.title_xpath || '无'}</code></td>
                <td><code>${rule.content_xpath || '无'}</code></td>
                <td><span class="status-indicator ${statusClass}">${statusText}</span></td>
                <td>
                    <button class="btn btn-small ${statusClass}" onclick="toggleCrawlerRule('${rule.id}')">
                        ${statusText === '启用' ? '禁用' : '启用'}
                    </button>
                    <button class="btn btn-small btn-danger" onclick="deleteCrawlerRule('${rule.id}')">
                        删除
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    rulesListElement.innerHTML = html;
}

// 切换爬虫规则状态
function toggleCrawlerRule(ruleId) {
    const rule = AppState.crawlerRules.find(r => r.id === ruleId);
    if (rule) {
        if (rule.is_enabled) {
            WebSocketClient.sendDisableCrawlerRuleRequest(ruleId);
        } else {
            WebSocketClient.sendEnableCrawlerRuleRequest(ruleId);
        }
    }
}

// 删除爬虫规则
function deleteCrawlerRule(ruleId) {
    if (confirm('确定要删除此爬虫规则吗？')) {
        WebSocketClient.sendDeleteCrawlerRuleRequest(ruleId);
    }
}

// 初始化模态框
function initializeModal() {
    // 获取DOM元素
    const modal = document.getElementById('data-card-modal');
    const closeModalBtn = document.querySelector('.close-modal');
    
    // 关闭模态框按钮点击事件
    closeModalBtn.addEventListener('click', function() {
        closeModal();
    });
    
    // 点击模态框外部关闭模态框
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeModal();
        }
    });
    
    // 按下ESC键关闭模态框
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeModal();
        }
    });
}

// 加载个人资料
function loadProfile() {
    // 获取DOM元素
    const profileUsername = document.getElementById('profile-username');
    const profilePermissionLevel = document.getElementById('profile-permission-level');
    
    // 显示用户信息
    if (AppState.currentUser) {
        profileUsername.textContent = AppState.currentUser.username;
        profilePermissionLevel.textContent = AppState.currentUser.permission_level;
    }
}

// 刷新数据管理页面
function refreshDataManagementPage() {
    // 清空显示的数据
    AppState.dataRecords = [];
    displayDataRecords();
    
    // 发送数据管理刷新请求
    const refreshRequest = {
        type: 'refresh_data_management'
    };
    
    if (!WebSocketClient.send(refreshRequest)) {
        showStatusMessage('发送数据管理刷新请求失败，请检查连接', 'error');
    }
}

// 刷新搜索源管理页面
function refreshSearchSourceManagementPage() {
    // 发送搜索源管理刷新请求
    const refreshRequest = {
        type: 'refresh_search_source_management'
    };
    
    if (!WebSocketClient.send(refreshRequest)) {
        showStatusMessage('发送搜索源管理刷新请求失败，请检查连接', 'error');
    }
}

// 显示搜索结果
function displaySearchResults() {
    // 获取DOM元素
    const searchResultsContainer = document.getElementById('search-results');
    const paginationContainer = document.getElementById('pagination');
    
    // 清空之前的内容
    searchResultsContainer.innerHTML = '';
    paginationContainer.innerHTML = '';
    
    if (AppState.searchResults.length === 0) {
        searchResultsContainer.innerHTML = '<p style="text-align: center; color: rgba(255, 255, 255, 0.6);">未找到任何搜索结果</p>';
        return;
    }
    
    // 获取当前页面的结果
    const currentPageResults = getCurrentPageResults();
    
    // 生成数据卡片
    currentPageResults.forEach(result => {
        const dataCard = createDataCard(result);
        searchResultsContainer.appendChild(dataCard);
    });
    
    // 生成分页控件
    generatePagination();
}

// 获取当前页面的结果
function getCurrentPageResults() {
    const startIndex = (AppState.currentPage - 1) * AppState.itemsPerPage;
    const endIndex = startIndex + AppState.itemsPerPage;
    return AppState.searchResults.slice(startIndex, endIndex);
}

// 创建数据卡片
function createDataCard(result) {
    const card = document.createElement('div');
    card.className = 'data-card';
    card.dataset.id = result.id;
    
    // 检查是否已选择该数据
    let isSelected = AppState.selectedItems.has(result.id);
    
    // 数据卡片内容 - 支持新的字段名称 cover_url
    const imageUrl = result.cover_url || result.image_url;
    let imageSection = '';
    
    // 只有当有图片URL时才显示图片
    if (imageUrl) {
        imageSection = `<img src="${imageUrl}" alt="${result.title}" class="data-card-image">`;
    }
    
    card.innerHTML = `
        <div class="data-card-checkbox-container">
            <input type="checkbox" class="data-card-checkbox" ${isSelected ? 'checked' : ''}>
        </div>
        ${imageSection}
        <div class="data-card-content">
            <h3 class="data-card-title">
                <a href="${result.url}" target="_blank">${result.title}</a>
            </h3>
            <p class="data-card-summary">${result.summary}</p>
            <span class="data-card-source">来源: ${result.data_source_info ? result.data_source_info.name : result.data_source}</span>
            ${result.data_source_info && result.data_source_info.description ? `<p class="data-card-source-description">${result.data_source_info.description}</p>` : ''}
        </div>
    `;
    
    // 为复选框添加点击事件（切换选择状态）
    const checkbox = card.querySelector('.data-card-checkbox');
    checkbox.addEventListener('click', function(e) {
        e.stopPropagation(); // 阻止事件冒泡到卡片
        // 实时计算选中状态
        const currentSelected = AppState.selectedItems.has(result.id);
        if (currentSelected) {
            AppState.selectedItems.delete(result.id);
        } else {
            AppState.selectedItems.add(result.id);
        }
    });
    
    // 为卡片添加点击事件（切换选择状态）
    card.addEventListener('click', function() {
        // 实时计算选中状态
        const currentSelected = AppState.selectedItems.has(result.id);
        if (currentSelected) {
            AppState.selectedItems.delete(result.id);
            checkbox.checked = false;
        } else {
            AppState.selectedItems.add(result.id);
            checkbox.checked = true;
        }
    });
    
    return card;
}

// 生成分页控件
function generatePagination() {
    const totalPages = Math.ceil(AppState.searchResults.length / AppState.itemsPerPage);
    const paginationContainer = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        return; // 不需要分页
    }
    
    // 上一页按钮
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '上一页';
    prevBtn.disabled = AppState.currentPage === 1;
    prevBtn.addEventListener('click', function() {
        if (AppState.currentPage > 1) {
            AppState.currentPage--;
            displaySearchResults();
        }
    });
    paginationContainer.appendChild(prevBtn);
    
    // 页码按钮
    for (let i = 1; i <= totalPages; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.className = i === AppState.currentPage ? 'active' : '';
        pageBtn.addEventListener('click', function() {
            AppState.currentPage = i;
            displaySearchResults();
        });
        paginationContainer.appendChild(pageBtn);
    }
    
    // 下一页按钮
    const nextBtn = document.createElement('button');
    nextBtn.textContent = '下一页';
    nextBtn.disabled = AppState.currentPage === totalPages;
    nextBtn.addEventListener('click', function() {
        if (AppState.currentPage < totalPages) {
            AppState.currentPage++;
            displaySearchResults();
        }
    });
    paginationContainer.appendChild(nextBtn);
}

// 更新数据卡片选择状态
function updateDataCardSelections() {
    const dataCards = document.querySelectorAll('.data-card');
    
    dataCards.forEach(card => {
        const id = card.dataset.id;
        
        if (AppState.selectedItems.has(id)) {
            card.style.borderColor = '#00d2ff';
            card.style.borderWidth = '2px';
        } else {
            card.style.borderColor = 'rgba(255, 255, 255, 0.1)';
            card.style.borderWidth = '1px';
        }
    });
}

// 显示数据记录
function displayDataRecords() {
    // 获取DOM元素
    const dataListContainer = document.getElementById('data-list');
    
    // 清空之前的内容
    dataListContainer.innerHTML = '';
    
    if (AppState.dataRecords.length === 0) {
        dataListContainer.innerHTML = '<p style="text-align: center; color: rgba(255, 255, 255, 0.6);">暂无数据记录</p>';
        return;
    }
    
    // 生成数据项
    AppState.dataRecords.forEach(record => {
        const dataItem = createDataItem(record);
        dataListContainer.appendChild(dataItem);
    });
}

// 从URL中提取域名
function extractDomain(url) {
    try {
        const hostname = new URL(url).hostname;
        // 移除www前缀
        return hostname.replace(/^www\./, '');
    } catch (error) {
        return '';
    }
}

// 创建数据项
function createDataItem(record) {
    const item = document.createElement('div');
    item.className = 'data-item';
    item.dataset.id = record.id;
    
    // 检查是否已选择该数据
    if (AppState.selectedItems.has(record.id)) {
        item.style.borderColor = '#00d2ff';
        item.style.borderWidth = '2px';
    }
    
    // 添加点击事件（切换选择状态）
    item.addEventListener('click', function() {
        if (AppState.selectedItems.has(record.id)) {
            AppState.selectedItems.delete(record.id);
            item.style.borderColor = 'rgba(255, 255, 255, 0.1)';
            item.style.borderWidth = '1px';
        } else {
            AppState.selectedItems.add(record.id);
            item.style.borderColor = '#00d2ff';
            item.style.borderWidth = '2px';
        }
    });
    
    // 添加双击事件（显示数据卡片详情）
    item.addEventListener('dblclick', function() {
        showDataCardDetail(record);
    });
    
    // 提取域名
    const domain = extractDomain(record.source_url);
    
    // 模拟采集和嗅探规则（实际应用中应从数据库获取）
    const collectRule = '默认采集规则';
    const sniffRule = '默认嗅探规则';
    
    // 数据项内容 - 使用表格布局确保各部分宽度固定
    item.innerHTML = `
        <div class="data-item-header">
            <h3>${record.title}</h3>
            ${domain ? `<p class="domain">域名: ${domain}</p>` : ''}
        </div>
        <div class="data-item-content">
            <div class="data-rules">
                <div class="rule-item">
                    <span class="rule-label">采集规则:</span>
                    <span class="rule-value">${collectRule}</span>
                </div>
                <div class="rule-item">
                    <span class="rule-label">嗅探规则:</span>
                    <span class="rule-value">${sniffRule}</span>
                </div>
            </div>
        </div>
        <div class="data-item-footer">
            <div class="data-meta">
                <span>来源: ${record.data_source} | 采集时间: ${record.collection_time}</span>
            </div>
            <div class="data-actions">
                <button class="action-btn collect-btn" onclick="collectData('${record.id}')">采集</button>
                <button class="action-btn sniff-btn" onclick="sniffData('${record.id}')">嗅探</button>
            </div>
        </div>
    `;
    
    return item;
}

// 采集功能（待实现）
function collectData(recordId) {
    console.log('采集数据:', recordId);
    // 显示提示信息
    showStatusMessage('采集功能将在后续版本实现', 'info');
}

// 嗅探功能（待实现）
function sniffData(recordId) {
    console.log('嗅探数据:', recordId);
    // 显示提示信息
    showStatusMessage('嗅探功能将在后续版本实现', 'info');
}

// 更新数据项选择状态
function updateDataItemSelections() {
    const dataItems = document.querySelectorAll('.data-item');
    
    dataItems.forEach(item => {
        const id = item.dataset.id;
        
        if (AppState.selectedItems.has(id)) {
            item.style.borderColor = '#00d2ff';
            item.style.borderWidth = '2px';
        } else {
            item.style.borderColor = 'rgba(255, 255, 255, 0.1)';
            item.style.borderWidth = '1px';
        }
    });
}

// 显示数据卡片详情
function showDataCardDetail(record) {
    // 获取DOM元素
    const modal = document.getElementById('data-card-modal');
    const modalDataCard = document.getElementById('modal-data-card');
    
    // 数据卡片内容
    let imageSection = '';
    
    // 只有当有图片URL时才显示图片
    if (record.image_url) {
        imageSection = `<img src="${record.image_url}" alt="${record.title}" class="data-card-image">`;
    }
    
    modalDataCard.innerHTML = `
        ${imageSection}
        <div class="data-card-content">
            <h3 class="data-card-title">
                <a href="${record.url}" target="_blank">${record.title}</a>
            </h3>
            <p class="data-card-summary">${record.summary}</p>
            <span class="data-card-source">来源: ${record.data_source}</span>
            <br>
            <span class="data-card-source">采集时间: ${record.collection_time}</span>
        </div>
    `;
    
    // 显示模态框
    modal.style.display = 'block';
}

// 关闭模态框
function closeModal() {
    const modal = document.getElementById('data-card-modal');
    modal.style.display = 'none';
}

// 显示搜索源
function displaySearchSources() {
    // 获取DOM元素
    const searchSourceListContainer = document.getElementById('search-source-list');
    
    // 清空之前的内容
    searchSourceListContainer.innerHTML = '';
    
    if (AppState.searchSources.length === 0) {
        searchSourceListContainer.innerHTML = '<p style="text-align: center; color: rgba(255, 255, 255, 0.6);">暂无搜索源</p>';
        return;
    }
    
    // 生成搜索源卡片
    AppState.searchSources.forEach(source => {
        const searchSourceCard = createSearchSourceCard(source);
        searchSourceListContainer.appendChild(searchSourceCard);
    });
}

// 创建搜索源卡片
function createSearchSourceCard(source) {
    const card = document.createElement('div');
    card.className = 'search-source-card';
    card.dataset.id = source.id;
    
    // 搜索源状态
    const statusClass = source.is_active ? 'status-active' : 'status-inactive';
    const statusText = source.is_active ? '已启用' : '已禁用';
    
    // 操作按钮
    let actionButton = '';
    if (AppState.currentUser.permission_level >= 3) {
        if (source.is_active) {
            actionButton = `<button class="btn btn-danger disable-source" data-id="${source.id}">禁用</button>`;
        } else {
            actionButton = `<button class="btn btn-primary enable-source" data-id="${source.id}">启用</button>`;
        }
    }
    
    // 搜索源卡片内容
    card.innerHTML = `
        <h3>${source.name}</h3>
        <p>${source.description || '暂无描述'}</p>
        <span class="search-source-status ${statusClass}">${statusText}</span>
        <br>
        <br>
        ${actionButton}
    `;
    
    // 添加操作按钮点击事件
    if (AppState.currentUser.permission_level >= 3) {
        const disableBtn = card.querySelector('.disable-source');
        const enableBtn = card.querySelector('.enable-source');
        
        if (disableBtn) {
            disableBtn.addEventListener('click', function() {
                disableSearchSource(source.id);
            });
        }
        
        if (enableBtn) {
            enableBtn.addEventListener('click', function() {
                enableSearchSource(source.id);
            });
        }
    }
    
    return card;
}

// 禁用搜索源
function disableSearchSource(sourceId) {
    // 发送搜索源禁用请求
    const disableRequest = {
        type: 'disable_search_source',
        data: {
            source_id: sourceId
        }
    };
    
    if (!WebSocketClient.send(disableRequest)) {
        showStatusMessage('发送搜索源禁用请求失败，请检查连接', 'error');
    }
}

// 启用搜索源
function enableSearchSource(sourceId) {
    // 发送搜索源启用请求
    const enableRequest = {
        type: 'enable_search_source',
        data: {
            source_id: sourceId
        }
    };
    
    if (!WebSocketClient.send(enableRequest)) {
        showStatusMessage('发送搜索源启用请求失败，请检查连接', 'error');
    }
}

// 显示状态消息
function showStatusMessage(message, type = 'info') {
    // 获取当前活跃页面的状态消息元素
    const activePage = document.querySelector('.page.active');
    if (!activePage) return;
    
    let statusElement;
    if (activePage.id === 'data-collection') {
        statusElement = document.getElementById('search-status');
    } else if (activePage.id === 'data-management') {
        statusElement = document.getElementById('data-management-status');
    } else if (activePage.id === 'search-source-management') {
        statusElement = document.getElementById('search-source-status');
    } else if (activePage.id === 'crawler-rule-management') {
        statusElement = document.getElementById('crawler-rule-status');
    }
    
    if (!statusElement) return;
    
    // 设置消息内容和样式
    statusElement.textContent = message;
    
    switch (type) {
        case 'success':
            statusElement.style.backgroundColor = 'rgba(76, 175, 80, 0.3)';
            statusElement.style.color = '#4caf50';
            break;
        case 'error':
            statusElement.style.backgroundColor = 'rgba(244, 67, 54, 0.3)';
            statusElement.style.color = '#f44336';
            break;
        case 'warning':
            statusElement.style.backgroundColor = 'rgba(255, 193, 7, 0.3)';
            statusElement.style.color = '#ffc107';
            break;
        case 'info':
        default:
            statusElement.style.backgroundColor = 'rgba(33, 150, 243, 0.3)';
            statusElement.style.color = '#2196f3';
            break;
    }
    
    // 3秒后自动隐藏消息
    setTimeout(function() {
        statusElement.textContent = '';
        statusElement.style.backgroundColor = '';
        statusElement.style.color = '';
    }, 3000);
}

// 页面卸载时断开WebSocket连接
window.addEventListener('beforeunload', function() {
    WebSocketClient.disconnect();
});