import sqlite3
import hashlib
import os

print(f'当前目录: {os.getcwd()}')
print(f'数据库文件存在: {os.path.exists("patients.db")}')

# 连接数据库
conn = sqlite3.connect('patients.db')
cursor = conn.cursor()

# 查看用户表结构
print('\n用户表结构:')
cursor.execute('PRAGMA table_info(users)')
for row in cursor.fetchall():
    print(row)

# 查看是否有管理员用户
print('\n所有用户:')
cursor.execute('SELECT * FROM users')
for row in cursor.fetchall():
    print(row)

# 查看患者表结构
print('\n患者表结构:')
cursor.execute('PRAGMA table_info(patients)')
for row in cursor.fetchall():
    print(row)

# 关闭数据库连接
conn.close()
print('\n测试完成')
