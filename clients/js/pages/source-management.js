// 搜索源管理页面逻辑
class SourceManagementPage {
    constructor() {
        this.sources = [];
        this.init();
    }
    
    init() {
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // 刷新按钮点击事件
        document.getElementById('refresh-sources-btn').addEventListener('click', () => {
            this.refreshSources();
        });
    }
    
    refreshSources() {
        // 发送刷新搜索源请求
        const refreshPacket = {
            type: 'refresh_sources'
        };
        ws.send(refreshPacket);
    }
    
    renderSourceList(sources) {
        this.sources = sources;
        const sourceListContainer = document.getElementById('source-list');
        
        if (sources.length === 0) {
            sourceListContainer.innerHTML = '<div class="no-sources">没有可用的搜索源</div>';
            return;
        }
        
        let sourceListHTML = '';
        sources.forEach(source => {
            // 为搜索源添加描述信息
            const descriptions = {
                '百度搜索': '百度搜索是中国最大的搜索引擎之一，提供丰富的搜索结果。',
                '雅安政府网站': '雅安政府网站是雅安市的官方网站，提供了关于雅安市的各种信息。'
            };
            const description = descriptions[source.name] || '该搜索源暂无描述信息。';
            
            // 为搜索源添加颜色标识
            const colors = {
                '百度搜索': '#3b82f6', // 蓝色
                '雅安政府网站': '#10b981' // 绿色
            };
            const color = colors[source.name] || '#6b7280'; // 默认灰色
            
            sourceListHTML += `
                <div class="source-card" style="border-left-color: ${color};">
                    <h3 style="color: ${color};">${source.name}</h3>
                    <div class="color-div" style="background-color: ${color}; width: 100%; height: 4px; margin-bottom: 10px;"></div>
                    <p>${description}</p>
                    <div class="status ${source.is_blacklisted ? 'disabled' : 'enabled'}">
                        ${source.is_blacklisted ? '已禁用' : '已启用'}
                    </div>
                    ${app.currentUser.permission_level >= 3 ? `
                        <button class="btn ${source.is_blacklisted ? 'btn-success' : 'btn-danger'} action-btn" 
                                data-id="${source.id}"
                                data-action="${source.is_blacklisted ? 'enable' : 'disable'}">
                            ${source.is_blacklisted ? '启用' : '禁用'}
                        </button>
                    ` : ''}
                </div>
            `;
        });
        
        sourceListContainer.innerHTML = sourceListHTML;
        
        // 添加操作按钮的事件监听器
        if (app.currentUser.permission_level >= 3) {
            document.querySelectorAll('.action-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const sourceId = e.target.getAttribute('data-id');
                    const action = e.target.getAttribute('data-action');
                    this.updateSourceStatus(sourceId, action);
                });
            });
        }
    }
    
    updateSourceStatus(sourceId, action) {
        // 发送更新搜索源状态的请求
        const updatePacket = {
            type: 'toggle_source',
            data: {
                source_id: sourceId,
                is_blacklisted: action === 'disable'
            }
        };
        
        ws.send(updatePacket);
    }
}

// 初始化搜索源管理页面
const sourceManagementPage = new SourceManagementPage();
window.sourceManagementPage = sourceManagementPage;