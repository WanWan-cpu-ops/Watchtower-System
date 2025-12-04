from database import Database

def register_user():
    """
    通过控制台注册用户
    """
    db = Database()
    
    print("智能瞭望系统 用户注册")
    print("=" * 50)
    
    # 获取用户名
    while True:
        username = input("请输入用户名: ").strip()
        if not username:
            print("用户名不能为空，请重新输入")
        else:
            # 检查用户名是否已存在
            if db.get_user(username):
                print("用户名已存在，请选择其他用户名")
            else:
                break
    
    # 获取密码
    while True:
        password = input("请输入密码: ").strip()
        if not password:
            print("密码不能为空，请重新输入")
        else:
            confirm_password = input("请确认密码: ").strip()
            if password != confirm_password:
                print("两次输入的密码不一致，请重新输入")
            else:
                break
    
    # 获取权限等级
    while True:
        permission_input = input("请输入权限等级 (0-4，默认0): ").strip()
        if not permission_input:
            permission_level = 0
            break
        else:
            try:
                permission_level = int(permission_input)
                if 0 <= permission_level <= 4:
                    break
                else:
                    print("权限等级必须在0-4之间，请重新输入")
            except ValueError:
                print("权限等级必须是整数，请重新输入")
    
    # 注册用户
    if db.add_user(username, password, permission_level):
        print("=" * 50)
        print(f"用户注册成功!")
        print(f"用户名: {username}")
        print(f"权限等级: {permission_level}")
    else:
        print("用户注册失败，请稍后重试")
    
    db.close()

if __name__ == "__main__":
    register_user()