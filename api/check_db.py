import sqlite3

# 连接数据库
conn = sqlite3.connect('patients.db')
cursor = conn.cursor()

print('=== 数据库检查 ===')

# 检查所有表
print('\n1. 所有表:')
cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\'')
tables = cursor.fetchall()
for table in tables:
    print(f'   - {table[0]}')

# 检查用户表结构
print('\n2. 用户表结构:')
cursor.execute('PRAGMA table_info(users)')
users_columns = cursor.fetchall()
for column in users_columns:
    print(f'   - {column}')

# 检查患者表结构
print('\n3. 患者表结构:')
cursor.execute('PRAGMA table_info(patients)')
patients_columns = cursor.fetchall()
for column in patients_columns:
    print(f'   - {column}')

# 检查用户数据
print('\n4. 用户数据:')
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()
for user in users:
    print(f'   - {user}')

# 检查管理员用户
print('\n5. 管理员用户:')
cursor.execute('SELECT * FROM users WHERE username=\'admin\'')
admin = cursor.fetchone()
if admin:
    print(f'   ✓ 管理员用户存在: {admin}')
else:
    print('   ✗ 管理员用户不存在')

# 关闭数据库连接
conn.close()
print('\n=== 检查完成 ===')
