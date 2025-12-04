// 数据管理页面逻辑
class DataManagementPage {
    constructor() {
        this.dataRecords = [];
        this.init();
    }
    
    init() {
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // 数据搜索按钮点击事件
        document.getElementById('data-search-btn').addEventListener('click', () => {
            this.searchData();
        });
        
        // 删除数据按钮点击事件
        document.getElementById('delete-data-btn').addEventListener('click', () => {
            this.deleteSelectedData();
        });
        
        // 分析数据按钮点击事件
        document.getElementById('analyze-data-btn').addEventListener('click', () => {
            this.analyzeSelectedData();
        });
        
        // 回车键搜索
        document.getElementById('data-search-content').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchData();
            }
        });
    }
    
    searchData() {
        const searchContent = document.getElementById('data-search-content').value.trim();
        const searchField = document.getElementById('search-field').value;
        
        // 发送数据搜索请求
        const searchPacket = {
            type: 'data_search',
            data: {
                content: searchContent,
                field: searchField
            }
        };
        
        ws.send(searchPacket);
    }
    
    renderDataRecords(records) {
        this.dataRecords = records;
        const recordsContainer = document.getElementById('data-records');
        
        if (records.length === 0) {
            recordsContainer.innerHTML = '<div class="no-records">没有找到数据记录</div>';
            return;
        }
        
        let recordsHTML = '';
        records.forEach(record => {
            recordsHTML += `
                <div class="data-record">
                    <input type="checkbox" data-id="${record.id}" class="record-checkbox">
                    <div class="data-record-info">
                        <h4>${record.title}</h4>
                        <p>${record.summary.substring(0, 100)}${record.summary.length > 100 ? '...' : ''}</p>
                        <p><strong>来源:</strong> ${record.source} | <strong>日期:</strong> ${new Date(record.created_at).toLocaleString()}</p>
                    </div>
                    <button class="btn btn-sm btn-info view-data-btn" data-id="${record.id}">查看</button>
                </div>
            `;
        });
        
        recordsContainer.innerHTML = recordsHTML;
        
        // 添加查看数据按钮的事件监听器
        document.querySelectorAll('.view-data-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const recordId = e.target.getAttribute('data-id');
                this.viewDataRecord(recordId);
            });
        });
    }
    
    viewDataRecord(recordId) {
        const record = this.dataRecords.find(r => r.id === recordId);
        if (!record) return;
        
        // 创建数据卡片HTML
        const dataCardHTML = `
            <img src="${record.image_url || 'https://via.placeholder.com/300x200?text=No+Image'}" alt="${record.title}">
            <div class="data-card-content">
                <h3><a href="${record.url}" target="_blank">${record.title}</a></h3>
                <p>${record.summary}</p>
                <div class="source">${record.source}</div>
                <p><strong>日期:</strong> ${new Date(record.created_at).toLocaleString()}</p>
            </div>
        `;
        
        // 更新模态框内容
        document.getElementById('modal-data-card').innerHTML = dataCardHTML;
        
        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('data-card-modal'));
        modal.show();
    }
    
    deleteSelectedData() {
        // 检查用户权限
        if (app.currentUser.permission_level < 2) {
            alert('您的权限不足，无法删除数据');
            return;
        }
        
        const selectedCheckboxes = document.querySelectorAll('.record-checkbox:checked');
        
        if (selectedCheckboxes.length === 0) {
            alert('请选择要删除的数据');
            return;
        }
        
        if (!confirm('确定要删除选中的数据吗？')) {
            return;
        }
        
        const selectedIds = Array.from(selectedCheckboxes).map(checkbox => checkbox.getAttribute('data-id'));
        
        // 发送删除请求
        const deletePacket = {
            type: 'data_delete',
            data: {
                selected_ids: selectedIds
            }
        };
        
        ws.send(deletePacket);
    }
    
    analyzeSelectedData() {
        const selectedCheckboxes = document.querySelectorAll('.record-checkbox:checked');
        
        if (selectedCheckboxes.length === 0) {
            alert('请选择要分析的数据');
            return;
        }
        
        const selectedIds = Array.from(selectedCheckboxes).map(checkbox => checkbox.getAttribute('data-id'));
        
        // 这里可以添加分析功能的实现
        alert('数据分析功能将在后续实现');
        
        // 发送分析请求（根据后续要求实现）
        /*
        const analyzePacket = {
            type: 'data_analyze',
            data: {
                selected_ids: selectedIds
            }
        };
        
        ws.send(analyzePacket);
        */
    }
}

// 初始化数据管理页面
const dataManagementPage = new DataManagementPage();
window.dataManagementPage = dataManagementPage;