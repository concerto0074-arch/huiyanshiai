import sqlite3
import hashlib
import json

# 连接到数据库
conn = sqlite3.connect('patients.db')
cursor = conn.cursor()

# 创建表（如果不存在）
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    age INTEGER,
    gender TEXT,
    risk_score REAL,
    risk_level TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

# 密码哈希函数
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 创建测试用户
test_users = [
    ('testuser', 'test123'),
    ('admin', 'admin123')
]

for username, password in test_users:
    # 检查用户是否已存在
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if not user:
        # 创建新用户
        hashed_password = hash_password(password)
        cursor.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            (username, hashed_password, 'admin' if username == 'admin' else 'user')
        )
        print(f"创建用户成功: {username}")
    else:
        print(f"用户已存在: {username}")

# 提交更改
conn.commit()

# 验证用户
print("\n验证用户:")
for username, password in test_users:
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    stored_password = cursor.fetchone()
    
    if stored_password:
        hashed_input = hash_password(password)
        if hashed_input == stored_password[0]:
            print(f"用户 {username} 验证成功")
        else:
            print(f"用户 {username} 验证失败")
    else:
        print(f"用户 {username} 不存在")

# 关闭连接
conn.close()

print("\n测试完成")
