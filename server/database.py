import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'telescope.db')
        self.log(f"数据库初始化: 路径={self.db_path}", 'INFO')
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.log(f"数据库目录检查完成: 目录={os.path.dirname(self.db_path)}", 'DEBUG')
        
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.log(f"数据库连接成功: 路径={self.db_path}", 'INFO')
            
            self.create_tables()
            self.log(f"数据库表结构检查完成", 'INFO')
        
        except Exception as e:
            self.log(f"数据库初始化失败: {str(e)}", 'CRITICAL')
            raise
    
    def log(self, message, level='INFO'):
        """
        数据库操作日志记录函数
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [DB] [{level}] {message}")
    
    def create_tables(self):
        try:
            # 创建用户表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    permission_level INTEGER NOT NULL DEFAULT 0
                )
            ''')
            self.log(f"用户表检查/创建完成", 'DEBUG')
            
            # 创建数据记录表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    image_url TEXT,
                    source_url TEXT NOT NULL,
                    data_source TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.log(f"数据记录表检查/创建完成", 'DEBUG')
            
            # 创建搜索源黑名单表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_source_blacklist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT UNIQUE NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.log(f"搜索源黑名单表检查/创建完成", 'DEBUG')
            
            # 创建爬虫规则表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS crawler_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    title_xpath TEXT NOT NULL,
                    content_xpath TEXT NOT NULL,
                    image_xpath TEXT,
                    url_xpath TEXT,
                    request_headers TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    enabled INTEGER NOT NULL DEFAULT 1
                )
            ''')
            self.log(f"爬虫规则表检查/创建完成", 'DEBUG')
            
            # 创建详细爬虫规则表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS crawler_detailed_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crawler_rule_id INTEGER NOT NULL,
                    field_name TEXT NOT NULL,
                    xpath TEXT NOT NULL,
                    extract_type TEXT DEFAULT 'text',  -- text, html, attribute
                    attribute_name TEXT,  -- 当extract_type为attribute时使用
                    is_required INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (crawler_rule_id) REFERENCES crawler_rules (id) ON DELETE CASCADE
                )
            ''')
            self.log(f"详细爬虫规则表检查/创建完成", 'DEBUG')
            
            self.conn.commit()
            self.log(f"数据库表结构提交完成", 'DEBUG')
        
        except Exception as e:
            self.log(f"数据库表结构创建失败: {str(e)}", 'ERROR')
            raise
    
    # 用户相关操作
    def add_user(self, username, password, permission_level=0):
        self.log(f"开始添加用户: 用户名={username}, 权限等级={permission_level}", 'INFO')
        
        try:
            self.cursor.execute('''
                INSERT INTO users (username, password, permission_level) 
                VALUES (?, ?, ?)
            ''', (username, password, permission_level))
            self.conn.commit()
            
            self.log(f"用户添加成功: 用户名={username}", 'INFO')
            return True
        
        except sqlite3.IntegrityError:
            self.log(f"用户添加失败: 用户名={username} 已存在", 'WARNING')
            return False
        
        except Exception as e:
            self.log(f"用户添加失败: 用户名={username} - 错误: {str(e)}", 'ERROR')
            return False
    
    def get_user(self, username):
        self.log(f"开始查询用户: 用户名={username}", 'DEBUG')
        
        try:
            self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = self.cursor.fetchone()
            
            if user:
                self.log(f"用户查询成功: 用户名={username}, 用户数据={user}", 'DEBUG')
            else:
                self.log(f"用户查询失败: 用户名={username} 不存在", 'DEBUG')
            
            return user
        
        except Exception as e:
            self.log(f"用户查询失败: 用户名={username} - 错误: {str(e)}", 'ERROR')
            return None
    
    # 数据记录相关操作
    def add_data_record(self, title, summary, image_url, source_url, data_source):
        self.log(f"开始添加数据记录: 标题={title}, 数据源={data_source}", 'DEBUG')
        
        try:
            self.cursor.execute('''
                INSERT INTO data_records (title, summary, image_url, source_url, data_source) 
                VALUES (?, ?, ?, ?, ?)
            ''', (title, summary, image_url, source_url, data_source))
            self.conn.commit()
            
            record_id = self.cursor.lastrowid
            self.log(f"数据记录添加成功: 记录ID={record_id}, 标题={title}", 'DEBUG')
            
            return record_id
        
        except Exception as e:
            self.log(f"数据记录添加失败: 标题={title} - 错误: {str(e)}", 'ERROR')
            return None
    
    def get_data_records(self, search_content=None, search_field=None):
        if search_content and search_field:
            self.log(f"开始查询数据记录: 搜索内容={search_content}, 搜索字段={search_field}", 'DEBUG')
            
            try:
                if search_field == 'title':
                    self.cursor.execute('SELECT * FROM data_records WHERE title LIKE ? ORDER BY created_at DESC', 
                                        ('%' + search_content + '%',))
                elif search_field == 'summary':
                    self.cursor.execute('SELECT * FROM data_records WHERE summary LIKE ? ORDER BY created_at DESC', 
                                        ('%' + search_content + '%',))
                elif search_field == 'data_source':
                    self.cursor.execute('SELECT * FROM data_records WHERE data_source LIKE ? ORDER BY created_at DESC', 
                                        ('%' + search_content + '%',))
                
                records = self.cursor.fetchall()
                self.log(f"数据记录查询完成: 搜索内容={search_content}, 搜索字段={search_field}, 结果数量={len(records)}", 'DEBUG')
                
                return records
            
            except Exception as e:
                self.log(f"数据记录查询失败: 搜索内容={search_content}, 搜索字段={search_field} - 错误: {str(e)}", 'ERROR')
                return []
        
        else:
            self.log(f"开始查询所有数据记录", 'DEBUG')
            
            try:
                self.cursor.execute('SELECT * FROM data_records ORDER BY created_at DESC')
                records = self.cursor.fetchall()
                
                self.log(f"所有数据记录查询完成: 结果数量={len(records)}", 'DEBUG')
                
                return records
            
            except Exception as e:
                self.log(f"所有数据记录查询失败: 错误: {str(e)}", 'ERROR')
                return []
    
    def delete_data_record(self, record_id):
        self.log(f"开始删除数据记录: 记录ID={record_id}", 'INFO')
        
        try:
            self.cursor.execute('DELETE FROM data_records WHERE id = ?', (record_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                self.log(f"数据记录删除成功: 记录ID={record_id}", 'INFO')
                return True
            else:
                self.log(f"数据记录删除失败: 记录ID={record_id} 不存在", 'WARNING')
                return False
        
        except Exception as e:
            self.log(f"数据记录删除失败: 记录ID={record_id} - 错误: {str(e)}", 'ERROR')
            return False
    
    # 搜索源黑名单相关操作
    def add_to_blacklist(self, source_id):
        self.log(f"开始添加搜索源到黑名单: 源ID={source_id}", 'INFO')
        
        try:
            self.cursor.execute('INSERT INTO search_source_blacklist (source_id) VALUES (?)', (source_id,))
            self.conn.commit()
            
            self.log(f"搜索源添加到黑名单成功: 源ID={source_id}", 'INFO')
            return True
        
        except sqlite3.IntegrityError:
            self.log(f"搜索源添加到黑名单失败: 源ID={source_id} 已在黑名单中", 'WARNING')
            return False
        
        except Exception as e:
            self.log(f"搜索源添加到黑名单失败: 源ID={source_id} - 错误: {str(e)}", 'ERROR')
            return False
    
    def remove_from_blacklist(self, source_id):
        self.log(f"开始从黑名单移除搜索源: 源ID={source_id}", 'INFO')
        
        try:
            self.cursor.execute('DELETE FROM search_source_blacklist WHERE source_id = ?', (source_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                self.log(f"搜索源从黑名单移除成功: 源ID={source_id}", 'INFO')
                return True
            else:
                self.log(f"搜索源从黑名单移除失败: 源ID={source_id} 不在黑名单中", 'WARNING')
                return False
        
        except Exception as e:
            self.log(f"搜索源从黑名单移除失败: 源ID={source_id} - 错误: {str(e)}", 'ERROR')
            return False
    
    def is_in_blacklist(self, source_id):
        self.log(f"开始检查搜索源是否在黑名单中: 源ID={source_id}", 'DEBUG')
        
        try:
            self.cursor.execute('SELECT 1 FROM search_source_blacklist WHERE source_id = ?', (source_id,))
            result = self.cursor.fetchone() is not None
            
            if result:
                self.log(f"搜索源在黑名单中: 源ID={source_id}", 'DEBUG')
            else:
                self.log(f"搜索源不在黑名单中: 源ID={source_id}", 'DEBUG')
            
            return result
        
        except Exception as e:
            self.log(f"检查搜索源是否在黑名单中失败: 源ID={source_id} - 错误: {str(e)}", 'ERROR')
            return False
    
    def get_blacklist(self):
        self.log(f"开始获取搜索源黑名单", 'DEBUG')
        
        try:
            self.cursor.execute('SELECT source_id FROM search_source_blacklist')
            blacklist = [row[0] for row in self.cursor.fetchall()]
            
            self.log(f"搜索源黑名单获取完成: 黑名单数量={len(blacklist)}, 黑名单={blacklist}", 'DEBUG')
            
            return blacklist
        
        except Exception as e:
            self.log(f"搜索源黑名单获取失败: 错误: {str(e)}", 'ERROR')
            return []
    
    # 爬虫规则相关操作
    def add_crawler_rule(self, source_id, source_name, title_xpath, content_xpath, image_xpath=None, url_xpath=None, request_headers=None):
        self.log(f"开始添加爬虫规则: 源ID={source_id}, 源名称={source_name}", 'INFO')
        
        try:
            # 确保request_headers不为None
            if request_headers is None:
                request_headers = '{}'
            
            self.cursor.execute('''
                INSERT INTO crawler_rules (source_id, source_name, title_xpath, content_xpath, image_xpath, url_xpath, request_headers)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (source_id, source_name, title_xpath, content_xpath, image_xpath, url_xpath, request_headers))
            self.conn.commit()
            
            rule_id = self.cursor.lastrowid
            self.log(f"爬虫规则添加成功: 规则ID={rule_id}, 源名称={source_name}", 'INFO')
            
            return rule_id
        
        except Exception as e:
            self.log(f"爬虫规则添加失败: 源名称={source_name} - 错误: {str(e)}", 'ERROR')
            return None
    
    def get_crawler_rule(self, rule_id):
        self.log(f"开始查询爬虫规则: 规则ID={rule_id}", 'DEBUG')
        
        try:
            self.cursor.execute('SELECT * FROM crawler_rules WHERE id = ?', (rule_id,))
            rule = self.cursor.fetchone()
            
            if rule:
                self.log(f"爬虫规则查询成功: 规则ID={rule_id}", 'DEBUG')
            else:
                self.log(f"爬虫规则查询失败: 规则ID={rule_id} 不存在", 'DEBUG')
            
            return rule
        
        except Exception as e:
            self.log(f"爬虫规则查询失败: 规则ID={rule_id} - 错误: {str(e)}", 'ERROR')
            return None
    
    def get_crawler_rules(self, source_id=None, enabled=None):
        query = 'SELECT * FROM crawler_rules WHERE 1=1'
        params = []
        
        if source_id:
            query += ' AND source_id = ?'
            params.append(source_id)
        
        if enabled is not None:
            query += ' AND enabled = ?'
            params.append(1 if enabled else 0)
        
        query += ' ORDER BY source_name ASC'
        
        self.log(f"开始查询爬虫规则: 源ID={source_id}, 启用状态={enabled}", 'DEBUG')
        
        try:
            self.cursor.execute(query, params)
            rules = self.cursor.fetchall()
            
            self.log(f"爬虫规则查询完成: 结果数量={len(rules)}", 'DEBUG')
            
            return rules
        
        except Exception as e:
            self.log(f"爬虫规则查询失败: 错误: {str(e)}", 'ERROR')
            return []
    
    def get_all_crawler_rules(self):
        """
        获取所有爬虫规则
        
        返回:
            list: 包含所有爬虫规则的列表
        """
        self.log(f"开始获取所有爬虫规则", 'DEBUG')
        
        try:
            self.cursor.execute('SELECT * FROM crawler_rules ORDER BY source_name ASC')
            rules = self.cursor.fetchall()
            
            self.log(f"所有爬虫规则查询完成: 结果数量={len(rules)}", 'DEBUG')
            
            return rules
        
        except Exception as e:
            self.log(f"获取所有爬虫规则失败: 错误: {str(e)}", 'ERROR')
            return []
    
    def update_crawler_rule(self, rule_id, source_id=None, source_name=None, title_xpath=None, content_xpath=None, image_xpath=None, url_xpath=None, request_headers=None):
        self.log(f"开始更新爬虫规则: 规则ID={rule_id}", 'INFO')
        
        try:
            # 先获取当前规则
            current_rule = self.get_crawler_rule(rule_id)
            if not current_rule:
                return False
            
            # 使用当前值作为默认值
            update_source_id = source_id if source_id is not None else current_rule[1]
            update_source_name = source_name if source_name is not None else current_rule[2]
            update_title_xpath = title_xpath if title_xpath is not None else current_rule[3]
            update_content_xpath = content_xpath if content_xpath is not None else current_rule[4]
            update_image_xpath = image_xpath if image_xpath is not None else current_rule[5]
            update_url_xpath = url_xpath if url_xpath is not None else current_rule[6]
            update_request_headers = request_headers if request_headers is not None else current_rule[7]
            
            self.cursor.execute('''
                UPDATE crawler_rules SET
                    source_id = ?, source_name = ?, title_xpath = ?, content_xpath = ?, image_xpath = ?, url_xpath = ?, request_headers = ?
                WHERE id = ?
            ''', (update_source_id, update_source_name, update_title_xpath, update_content_xpath, update_image_xpath, update_url_xpath, update_request_headers, rule_id))
            self.conn.commit()
            
            self.log(f"爬虫规则更新成功: 规则ID={rule_id}", 'INFO')
            
            return True
        
        except Exception as e:
            self.log(f"爬虫规则更新失败: 规则ID={rule_id} - 错误: {str(e)}", 'ERROR')
            return False
    
    def delete_crawler_rule(self, rule_id):
        self.log(f"开始删除爬虫规则: 规则ID={rule_id}", 'INFO')
        
        try:
            self.cursor.execute('DELETE FROM crawler_rules WHERE id = ?', (rule_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                self.log(f"爬虫规则删除成功: 规则ID={rule_id}", 'INFO')
                return True
            else:
                self.log(f"爬虫规则删除失败: 规则ID={rule_id} 不存在", 'WARNING')
                return False
        
        except Exception as e:
            self.log(f"爬虫规则删除失败: 规则ID={rule_id} - 错误: {str(e)}", 'ERROR')
            return False
    
    def enable_crawler_rule(self, rule_id):
        self.log(f"开始启用爬虫规则: 规则ID={rule_id}", 'INFO')
        
        try:
            self.cursor.execute('UPDATE crawler_rules SET enabled = 1 WHERE id = ?', (rule_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                self.log(f"爬虫规则启用成功: 规则ID={rule_id}", 'INFO')
                return True
            else:
                self.log(f"爬虫规则启用失败: 规则ID={rule_id} 不存在", 'WARNING')
                return False
        
        except Exception as e:
            self.log(f"爬虫规则启用失败: 规则ID={rule_id} - 错误: {str(e)}", 'ERROR')
            return False
    
    def disable_crawler_rule(self, rule_id):
        self.log(f"开始禁用爬虫规则: 规则ID={rule_id}", 'INFO')
        
        try:
            self.cursor.execute('UPDATE crawler_rules SET enabled = 0 WHERE id = ?', (rule_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                self.log(f"爬虫规则禁用成功: 规则ID={rule_id}", 'INFO')
                return True
            else:
                self.log(f"爬虫规则禁用失败: 规则ID={rule_id} 不存在", 'WARNING')
                return False
        
        except Exception as e:
            self.log(f"爬虫规则禁用失败: 规则ID={rule_id} - 错误: {str(e)}", 'ERROR')
            return False
    
    # 详细爬虫规则相关操作
    def add_crawler_detailed_rule(self, crawler_rule_id, field_name, xpath, extract_type='text', attribute_name=None, is_required=0):
        self.log(f"开始添加详细爬虫规则: 主规则ID={crawler_rule_id}, 字段名={field_name}", 'INFO')
        
        try:
            self.cursor.execute('''
                INSERT INTO crawler_detailed_rules (crawler_rule_id, field_name, xpath, extract_type, attribute_name, is_required)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (crawler_rule_id, field_name, xpath, extract_type, attribute_name, is_required))
            self.conn.commit()
            
            rule_id = self.cursor.lastrowid
            self.log(f"详细爬虫规则添加成功: 规则ID={rule_id}, 字段名={field_name}", 'INFO')
            
            return rule_id
        
        except Exception as e:
            self.log(f"详细爬虫规则添加失败: 字段名={field_name} - 错误: {str(e)}", 'ERROR')
            return None
    
    def get_crawler_detailed_rules(self, crawler_rule_id):
        self.log(f"开始查询详细爬虫规则: 主规则ID={crawler_rule_id}", 'DEBUG')
        
        try:
            self.cursor.execute('SELECT * FROM crawler_detailed_rules WHERE crawler_rule_id = ?', (crawler_rule_id,))
            rules = self.cursor.fetchall()
            
            self.log(f"详细爬虫规则查询完成: 主规则ID={crawler_rule_id}, 结果数量={len(rules)}", 'DEBUG')
            
            return rules
        
        except Exception as e:
            self.log(f"详细爬虫规则查询失败: 主规则ID={crawler_rule_id} - 错误: {str(e)}", 'ERROR')
            return []
    
    def update_crawler_detailed_rule(self, rule_id, field_name=None, xpath=None, extract_type=None, attribute_name=None, is_required=None):
        self.log(f"开始更新详细爬虫规则: 规则ID={rule_id}", 'INFO')
        
        try:
            # 先获取当前规则
            current_rule = self.get_crawler_detailed_rule(rule_id)
            if not current_rule:
                return False
            
            # 使用当前值作为默认值
            update_field_name = field_name if field_name is not None else current_rule[2]
            update_xpath = xpath if xpath is not None else current_rule[3]
            update_extract_type = extract_type if extract_type is not None else current_rule[4]
            update_attribute_name = attribute_name if attribute_name is not None else current_rule[5]
            update_is_required = is_required if is_required is not None else current_rule[6]
            
            self.cursor.execute('''
                UPDATE crawler_detailed_rules SET
                    field_name = ?, xpath = ?, extract_type = ?, attribute_name = ?, is_required = ?
                WHERE id = ?
            ''', (update_field_name, update_xpath, update_extract_type, update_attribute_name, update_is_required, rule_id))
            self.conn.commit()
            
            self.log(f"详细爬虫规则更新成功: 规则ID={rule_id}", 'INFO')
            
            return True
        
        except Exception as e:
            self.log(f"详细爬虫规则更新失败: 规则ID={rule_id} - 错误: {str(e)}", 'ERROR')
            return False
    
    def delete_crawler_detailed_rule(self, rule_id):
        self.log(f"开始删除详细爬虫规则: 规则ID={rule_id}", 'INFO')
        
        try:
            self.cursor.execute('DELETE FROM crawler_detailed_rules WHERE id = ?', (rule_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                self.log(f"详细爬虫规则删除成功: 规则ID={rule_id}", 'INFO')
                return True
            else:
                self.log(f"详细爬虫规则删除失败: 规则ID={rule_id} 不存在", 'WARNING')
                return False
        
        except Exception as e:
            self.log(f"详细爬虫规则删除失败: 规则ID={rule_id} - 错误: {str(e)}", 'ERROR')
            return False
    
    def delete_crawler_detailed_rules_by_rule_id(self, crawler_rule_id):
        self.log(f"开始删除详细爬虫规则: 主规则ID={crawler_rule_id}", 'INFO')
        
        try:
            self.cursor.execute('DELETE FROM crawler_detailed_rules WHERE crawler_rule_id = ?', (crawler_rule_id,))
            self.conn.commit()
            
            self.log(f"详细爬虫规则删除成功: 主规则ID={crawler_rule_id}, 删除数量={self.cursor.rowcount}", 'INFO')
            return True
        
        except Exception as e:
            self.log(f"详细爬虫规则删除失败: 主规则ID={crawler_rule_id} - 错误: {str(e)}", 'ERROR')
            return False
    
    def get_crawler_detailed_rule(self, rule_id):
        self.log(f"开始查询单个详细爬虫规则: 规则ID={rule_id}", 'DEBUG')
        
        try:
            self.cursor.execute('SELECT * FROM crawler_detailed_rules WHERE id = ?', (rule_id,))
            rule = self.cursor.fetchone()
            
            if rule:
                self.log(f"详细爬虫规则查询成功: 规则ID={rule_id}", 'DEBUG')
            else:
                self.log(f"详细爬虫规则查询失败: 规则ID={rule_id} 不存在", 'DEBUG')
            
            return rule
        
        except Exception as e:
            self.log(f"详细爬虫规则查询失败: 规则ID={rule_id} - 错误: {str(e)}", 'ERROR')
            return None
    
    def close(self):
        try:
            self.conn.close()
            self.log(f"数据库连接已关闭", 'INFO')
        
        except Exception as e:
            self.log(f"数据库连接关闭失败: {str(e)}", 'ERROR')