import sqlite3
import hashlib
from database import init_db, add_user, User, get_user_by_username

# 密码哈希函数
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 初始化数据库
init_db()

# 检查是否已存在管理员用户
admin_user = get_user_by_username('admin')

if admin_user:
    print("管理员用户已存在")
else:
    # 创建初始管理员用户
    hashed_password = hash_password('admin123')  # 初始管理员密码
    new_admin = User(username='admin', password=hashed_password, email='admin@example.com', role='admin')
    admin_id = add_user(new_admin)
    print(f"初始管理员用户创建成功，ID: {admin_id}")
    print("用户名: admin")
    print("密码: admin123")
    print("请登录后立即修改密码")
