import sqlite3
import hashlib
import os

print(f'当前目录: {os.getcwd()}')
print(f'数据库文件存在: {os.path.exists("patients.db")}')

# 连接数据库
conn = sqlite3.connect('patients.db')
cursor = conn.cursor()
print('连接数据库成功')

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
print('用户表创建/检查成功')

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
print('患者表创建/检查成功')

# 提交创建表的操作
conn.commit()

# 创建管理员用户
hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
cursor.execute(
    'INSERT OR IGNORE INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
    ('admin', hashed_password, 'admin@example.com', 'admin')
)
conn.commit()
print('管理员用户创建/检查成功')

# 检查管理员用户是否创建成功
cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
admin_user = cursor.fetchone()
if admin_user:
    print(f'管理员用户存在: {admin_user}')
else:
    print('管理员用户创建失败')

# 关闭数据库连接
conn.close()
print('数据库连接关闭')
print('初始化完成')
