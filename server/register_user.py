import sqlite3
import bcrypt

# 连接数据库
conn = sqlite3.connect('telescope.db')
cursor = conn.cursor()

def register_user():
    print("=== 智能瞭望数据分析处理系统 用户注册 ===")
    
    # 获取用户名
    while True:
        username = input("请输入用户名: ").strip()
        if username:
            # 检查用户名是否已存在
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                print("该用户名已存在，请选择其他用户名。")
            else:
                break
        else:
            print("用户名不能为空，请重新输入。")
    
    # 获取密码
    while True:
        password = input("请输入密码: ").strip()
        if password:
            confirm_password = input("请再次确认密码: ").strip()
            if password == confirm_password:
                # 对密码进行哈希处理
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                break
            else:
                print("两次输入的密码不一致，请重新输入。")
        else:
            print("密码不能为空，请重新输入。")
    
    # 获取权限等级
    while True:
        try:
            permission_level = int(input("请输入权限等级 (0-4): "))
            if 0 <= permission_level <= 4:
                break
            else:
                print("权限等级必须在0-4之间，请重新输入。")
        except ValueError:
            print("无效的输入，请输入一个整数。")
    
    # 插入用户数据
    cursor.execute(
        "INSERT INTO users (username, password, permission_level) VALUES (?, ?, ?)",
        (username, hashed_password.decode('utf-8'), permission_level)
    )
    
    # 保存更改
    conn.commit()
    
    print(f"\n用户 '{username}' 注册成功！权限等级: {permission_level}")

if __name__ == "__main__":
    register_user()
    
    # 关闭数据库连接
    conn.close()
