import sqlite3
import os

print("测试数据库连接...")

# 检查数据库文件是否存在
db_path = 'patients.db'
print(f"数据库文件路径: {os.path.abspath(db_path)}")
print(f"数据库文件是否存在: {os.path.exists(db_path)}")

# 尝试连接数据库
try:
    conn = sqlite3.connect(db_path)
    print("数据库连接成功")
    
    # 获取游标
    cursor = conn.cursor()
    print("获取游标成功")
    
    # 查询所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"数据库中的表: {[table[0] for table in tables]}")
    
    # 关闭连接
    conn.close()
    print("数据库连接关闭成功")
except Exception as e:
    print(f"数据库操作失败: {e}")
    import traceback
    traceback.print_exc()
