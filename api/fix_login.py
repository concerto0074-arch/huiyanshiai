import sqlite3
import hashlib
import os

# 检查并创建数据库
print("当前工作目录:", os.getcwd())
db_path = 'patients.db'
print(f"数据库文件路径: {db_path}")
print(f"数据库文件存在: {os.path.exists(db_path)}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
print("成功连接数据库")

# 创建用户表
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')
print("用户表创建/检查成功")

# 创建患者表
cursor.execute('''
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    mean_radius REAL,
    mean_texture REAL,
    mean_perimeter REAL,
    mean_area REAL,
    mean_smoothness REAL,
    diagnosis TEXT,
    probability REAL,
    risk_level TEXT,
    summary TEXT,
    analysis TEXT,
    suggestions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
''')
print("患者表创建/检查成功")

# 创建测试用户
print("\n创建测试用户...")

# 创建普通用户
hashed_password = hashlib.sha256('test123'.encode()).hexdigest()
cursor.execute(
    'INSERT OR IGNORE INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
    ('testuser', hashed_password, 'test@example.com', 'user')
)
print("普通用户创建/检查成功")

# 创建管理员用户
hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
cursor.execute(
    'INSERT OR IGNORE INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
    ('admin', hashed_password, 'admin@example.com', 'admin')
)
print("管理员用户创建/检查成功")

# 提交更改
conn.commit()

# 检查用户是否创建成功
print("\n检查用户数据...")
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()
for user in users:
    print(f"用户: ID={user[0]}, 用户名={user[1]}, 角色={user[4]}")

# 测试密码哈希
print("\n测试密码哈希...")
passwords_to_test = ['test123', 'admin123']
for password in passwords_to_test:
    hashed = hashlib.sha256(password.encode()).hexdigest()
    print(f"密码 '{password}' 的哈希值: {hashed}")
    
    # 检查数据库中是否有匹配的哈希值
    cursor.execute('SELECT * FROM users WHERE password = ?', (hashed,))
    matching_users = cursor.fetchall()
    if matching_users:
        print(f"  在数据库中找到匹配的用户: {[u[1] for u in matching_users]}")
    else:
        print("  在数据库中没有找到匹配的用户")

# 关闭数据库连接
conn.close()
print("\n修复完成！")
print("\n登录信息:")
print("普通用户: 用户名=testuser, 密码=test123")
print("管理员用户: 用户名=admin, 密码=admin123")
