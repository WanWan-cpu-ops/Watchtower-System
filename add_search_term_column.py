import sqlite3
import os

# 数据库路径
db_path = r"E:\Watchtower-System-main\Watchtower-System-main\data\telescope.db"

# 连接数据库
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("数据库连接成功")
    
    # 添加search_term字段
    try:
        cursor.execute("ALTER TABLE data_records ADD COLUMN search_term TEXT")
        conn.commit()
        print("成功添加search_term字段")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("search_term字段已存在")
        else:
            raise
    
    # 查询数据记录表结构
    cursor.execute("PRAGMA table_info(data_records)")
    columns = cursor.fetchall()
    print("\n更新后的数据表结构:")
    for column in columns:
        print(f"{column[1]} - {column[2]}")
    
    # 查询前5条记录
    cursor.execute("SELECT * FROM data_records LIMIT 5")
    records = cursor.fetchall()
    print(f"\n前5条记录 (共{len(records)}条):")
    for record in records:
        print(f"ID: {record[0]}, 标题: {record[1]}, 列数: {len(record)}")
        if len(record) >= 8:
            print(f"  搜索词: {record[6]}, 时间: {record[7]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"数据库操作错误: {e}")