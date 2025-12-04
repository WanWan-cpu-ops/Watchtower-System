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
    
    def close(self):
        try:
            self.conn.close()
            self.log(f"数据库连接已关闭", 'INFO')
        
        except Exception as e:
            self.log(f"数据库连接关闭失败: {str(e)}", 'ERROR')