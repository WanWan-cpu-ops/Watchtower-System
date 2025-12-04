import sqlite3
import bcrypt

# 创建数据库连接
conn = sqlite3.connect('telescope.db')
cursor = conn.cursor()

# 创建用户表
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    permission_level INTEGER NOT NULL DEFAULT 0,
    real_name TEXT,
    id_card TEXT,
    phone_number TEXT,
    verification_status INTEGER DEFAULT 0,
    verification_reason TEXT,
    verification_time TIMESTAMP,
    id_card_encrypted TEXT,
    phone_number_encrypted TEXT
)''')

# 创建数据记录表
cursor.execute('''
CREATE TABLE IF NOT EXISTS data_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    summary TEXT,
    image_url TEXT,
    url TEXT NOT NULL,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 创建搜索源表
cursor.execute('''
CREATE TABLE IF NOT EXISTS search_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    is_blacklisted INTEGER DEFAULT 0
)
''')

# 保存更改并关闭连接
conn.commit()
conn.close()

print("数据库初始化完成！")
