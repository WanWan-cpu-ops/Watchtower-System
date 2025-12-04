# 智能瞭望系统

一个基于B/S结构的Web应用，用于通过爬虫技术采集多个网页信息并进行人工数据筛选、数据存储、数据管理和数据分析。

## 功能模块

### 1. 注册登录
- 使用控制台脚本进行用户注册
- 登录页面验证用户名和密码
- 用户权限等级管理（0-4）

### 2. 数据采集
- 输入搜索内容和筛选页数
- 调用所有可用的搜索源进行数据爬取
- 搜索结果以数据卡片形式展示（每行3个，最多6行）
- 分页显示搜索结果
- 选择数据进行筛选入库

### 3. 搜索源管理
- 以卡片形式展示所有可用的搜索源
- 查看搜索源状态（已启用/已禁用）
- 权限等级大于等于3的用户可以禁用和启用搜索源

### 4. 数据管理
- 搜索数据库中的数据记录
- 以列表形式展示数据记录
- 查看数据卡片详情
- 权限等级大于等于2的用户可以删除数据
- 选择数据进行数据分析（后续版本实现）

### 5. 个人资料
- 显示登录用户的信息
- 退出登录

## 技术栈

- **前端**：HTML5 + CSS3 + JavaScript
- **后端**：Python 3
- **通信**：WebSocket
- **数据库**：SQLite
- **爬取**：requests + BeautifulSoup

## 项目结构

```
Telescope/
├── client/                 # 前端代码
│   ├── css/               # 样式文件
│   │   └── style.css     # 主样式文件
│   ├── js/                # JavaScript文件
│   │   ├── websocket.js  # WebSocket通信模块
│   │   ├── login.js       # 登录页面脚本
│   │   └── app.js         # 主应用脚本
│   ├── login.html         # 登录页面
│   └── index.html         # 主应用页面
├── data/                   # 数据目录
│   └── telescope.db       # SQLite数据库文件
├── search_sources/         # 搜索源目录
│   ├── __pycache__/       # Python缓存目录
│   ├── baidu.py           # 百度搜索源
│   ├── yaanGov.py         # 雅安政府网站搜索源
│   ├── html_cache/        # HTML缓存目录
│   ├── proceeded_pages/   # 已处理页面目录
│   ├── search_cache/      # 搜索结果缓存目录
│   └── search_source_config.json  # 搜索源配置文件
├── server/                 # 后端代码
│   ├── __pycache__/       # Python缓存目录
│   ├── database.py         # 数据库操作类
│   ├── C2SPackageHelper.py# 服务端到客户端数据包封装
│   ├── register_user.py    # 用户注册脚本
│   ├── search_source_manager.py  # 搜索源管理器
│   ├── websocket_server.py# WebSocket服务器
│   └── ResetResultData.py  # 数据重置工具
├── start.bat              # Windows启动批处理
├── start_server.py        # 简单服务器启动脚本
├── start_full_server.py   # 完整服务器启动脚本
├── requirements.txt       # Python依赖项列表
└── README.md              # 项目说明文档
```

## 安装和运行

### 1. 环境准备
- Python 3.7+ 
- 虚拟环境（推荐）

### 2. 安装依赖
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate.bat
# Linux/macOS
source venv/bin/activate

# 安装依赖项
pip install -r requirements.txt
```

### 3. 注册用户
```bash
python -m server.register_user
```

### 4. 启动服务器
```bash
python start_server.py
```

### 5. 访问应用
在浏览器中访问 `http://localhost:8000/client/login.html`

## 使用说明

### 1. 用户权限等级
- 0：普通用户（只能查看和筛选数据）
- 1：高级用户（普通用户权限 + 数据分析）
- 2：管理员（高级用户权限 + 删除数据）
- 3：超级管理员（管理员权限 + 管理搜索源）
- 4：系统管理员（所有权限）

### 2. 搜索源规范
- 搜索源必须以Python脚本形式存在于 `search_sources` 目录中
- 搜索源脚本必须包含 `main` 函数作为调用入口
- `main` 函数参数：`search_content`（搜索内容）、`max_pages`（最大页数）
- `main` 函数返回值：`(status, results)`，其中 `status` 为 `success` 或 `failed`，`results` 为结果列表
- 结果列表中的每个元素必须包含：`title`（标题）、`summary`（摘要）、`image_url`（图片URL）、`url`（源URL）、`data_source`（数据来源）

### 3. 数据筛选
- 在数据采集页面，选择要筛选的数据卡片
- 点击「筛选选中数据」按钮
- 系统将把选中的数据存入数据库

### 4. 数据管理
- 在数据管理页面，可以搜索数据库中的数据
- 可以选择数据进行删除（需要管理员权限）
- 可以选择数据进行数据分析（后续版本实现）

### 5. 搜索源管理
- 在搜索源管理页面，可以查看所有可用的搜索源
- 可以禁用或启用搜索源（需要超级管理员权限）

## 开发说明

### 1. 添加新的搜索源
1. 在 `search_sources` 目录中创建一个新的Python脚本
2. 实现 `main` 函数，按照搜索源规范返回结果
3. 重启服务器，新的搜索源将自动加载

### 2. 扩展功能
- 数据分析功能：在 `server` 目录中创建分析模块，在 `app.js` 中添加分析相关的前端代码
- 数据导出功能：在 `server` 目录中创建导出模块，在前端添加导出按钮和相关逻辑
- 用户管理功能：在前端添加用户管理页面，在 `server` 目录中创建用户管理模块

## 许可证

MIT License

## 作者

智能瞭望系统团队