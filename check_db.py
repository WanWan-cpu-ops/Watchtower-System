import sqlite3
import os

# 检查两个数据库文件
db_files = ['telescope.db', 'client/data/telescope.db']

for db_file in db_files:
    if os.path.exists(db_file):
        print(f'\n=== 检查数据库: {db_file} ===')
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f'数据库中的表: {[table[0] for table in tables]}')
        
        # 检查crawler_rules表
        if any('crawler_rules' in table[0] for table in tables):
            print('\ncrawler_rules表结构：')
            cursor.execute('PRAGMA table_info(crawler_rules);')
            rows = cursor.fetchall()
            print('ID | 列名 | 类型 | 非空 | 默认值 | 主键')
            for row in rows:
                print(f'{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}')
            
            # 查询所有规则
            print('\n所有爬虫规则：')
            cursor.execute('SELECT * FROM crawler_rules;')
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        
        # 检查crawler_detailed_rules表
        if any('crawler_detailed_rules' in table[0] for table in tables):
            print('\ncrawler_detailed_rules表结构：')
            cursor.execute('PRAGMA table_info(crawler_detailed_rules);')
            rows = cursor.fetchall()
            print('ID | 列名 | 类型 | 非空 | 默认值 | 主键')
            for row in rows:
                print(f'{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}')
        
        conn.close()
    else:
        print(f'\n=== 数据库不存在: {db_file} ===')