// 数据采集页面逻辑
class DataCollectionPage {
    constructor() {
        this.searchResults = [];
        this.init();
    }
    
    init() {
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // 开始搜索按钮点击事件
        document.getElementById('start-search-btn').addEventListener('click', () => {
            this.startSearch();
        });
        
        // 筛选按钮点击事件
        document.getElementById('filter-btn').addEventListener('click', () => {
            this.filterSelectedData();
        });
        
        // 回车键搜索
        document.getElementById('search-content').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.startSearch();
            }
        });
        
        document.getElementById('page-count').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.startSearch();
            }
        });
    }
    
    startSearch() {
        const searchContent = document.getElementById('search-content').value.trim();
        const pageCount = parseInt(document.getElementById('page-count').value);
        
        if (!searchContent) {
            alert('请输入搜索内容');
            return;
        }
        
        if (!pageCount || pageCount < 1 || pageCount > 10) {
            alert('请输入1-10之间的页数');
            return;
        }
        
        // 发送搜索请求
        const searchPacket = {
            type: 'search',
            data: {
                content: searchContent,
                page_count: pageCount
            }
        };
        
        ws.send(searchPacket);
    }
    
    renderSearchResults() {
        const resultsContainer = document.getElementById('search-results');
        const currentResults = app.getCurrentPageResults();
        
        if (currentResults.length === 0) {
            resultsContainer.innerHTML = '<div class="no-results">没有找到搜索结果</div>';
            return;
        }
        
        let resultsHTML = '';
        currentResults.forEach((result, index) => {
            resultsHTML += `
                <div class="data-card">
                    <input type="checkbox" data-id="${result.id}" class="result-checkbox">
                    <img src="${result.image_url || 'https://via.placeholder.com/300x200?text=No+Image'}" alt="${result.title}">
                    <div class="data-card-content">
                        <h3><a href="${result.url}" target="_blank">${result.title}</a></h3>
                        <p>${result.summary}</p>
                        <div class="source">${result.source}</div>
                    </div>
                </div>
            `;
        });
        
        resultsContainer.innerHTML = resultsHTML;
    }
    
    filterSelectedData() {
        const selectedCheckboxes = document.querySelectorAll('.result-checkbox:checked');
        
        if (selectedCheckboxes.length === 0) {
            alert('请选择要筛选的数据');
            return;
        }
        
        const selectedIds = Array.from(selectedCheckboxes).map(checkbox => checkbox.getAttribute('data-id'));
        
        // 发送筛选请求
        const filterPacket = {
            type: 'filter',
            data: {
                selected_ids: selectedIds
            }
        };
        
        ws.send(filterPacket);
    }
}

// 初始化数据采集页面
const dataCollectionPage = new DataCollectionPage();
window.dataCollectionPage = dataCollectionPage;