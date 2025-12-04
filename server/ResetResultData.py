import sqlite3
import os
from datetime import datetime

def log(message, level='INFO'):
    """日志记录函数"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}")

def reset_data_records_database():
    """重置数据记录数据库"""
    # 数据库路径
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'telescope.db')
    log(f"数据库路径: {db_path}")
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        log(f"数据库文件不存在: {db_path}", 'ERROR')
        return False
    
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        log(f"数据库连接成功")
        
        # 删除数据记录表
        log(f"开始删除数据记录表")
        cursor.execute('DROP TABLE IF EXISTS data_records')
        conn.commit()
        log(f"数据记录表删除成功")
        
        # 重新创建数据记录表
        log(f"开始重新创建数据记录表")
        cursor.execute('''
            CREATE TABLE data_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                image_url TEXT,
                source_url TEXT NOT NULL,
                data_source TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        log(f"数据记录表重新创建成功")
        
        # 关闭数据库连接
        conn.close()
        log(f"数据库连接已关闭")
        
        log(f"数据记录数据库重置成功")
        return True
    
    except Exception as e:
        log(f"数据记录数据库重置失败: {str(e)}", 'ERROR')
        return False

if __name__ == "__main__":
    log(f"开始重置数据记录数据库")
    success = reset_data_records_database()
    if success:
        log(f"数据记录数据库重置成功")
    else:
        log(f"数据记录数据库重置失败")
