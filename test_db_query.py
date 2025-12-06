import sqlite3
import os

# 数据库路径
db_path = r"E:\Watchtower-System-main\Watchtower-System-main\data\telescope.db"

# 检查数据库文件是否存在
if not os.path.exists(db_path):
    print("数据库文件不存在")
    exit()

# 连接数据库
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("数据库连接成功")
    
    # 查询数据记录表结构
    cursor.execute("PRAGMA table_info(data_records)")
    columns = cursor.fetchall()
    print("\n数据表结构:")
    for column in columns:
        print(f"{column[1]} - {column[2]}")
    
    # 查询数据记录数量
    cursor.execute("SELECT COUNT(*) FROM data_records")
    count = cursor.fetchone()[0]
    print(f"\n数据记录总数: {count}")
    
    # 查询前5条记录
    cursor.execute("SELECT * FROM data_records LIMIT 5")
    records = cursor.fetchall()
    print("\n前5条记录:")
    for record in records:
        print(f"ID: {record[0]}, 标题: {record[1]}, 搜索词: {record[6]}, 时间: {record[7]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"数据库操作错误: {e}")