"""
慧眼识癌 - Supabase 种子数据插入脚本
用法: python supabase/seed_users.py
功能: 向 Supabase users 表插入默认管理员和测试用户（密码 bcrypt 哈希）
"""
import os
import sys
import requests
import bcrypt
from dotenv import load_dotenv

# 加载项目根目录的 .env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

SUPABASE_URL = os.getenv('SUPABASE_URL')
ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not ANON_KEY:
    print("❌ 缺少 SUPABASE_URL 或 SUPABASE_ANON_KEY，请检查 .env 文件")
    sys.exit(1)

HEADERS = {
    'apikey': ANON_KEY,
    'Authorization': f'Bearer {ANON_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

SEED_USERS = [
    {
        'username': 'admin',
        'email': 'admin@huiyanshiai.com',
        'password': 'admin123',
        'role': 'admin',
        'phone': ''
    },
    {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'test123456',
        'role': 'user',
        'phone': ''
    }
]


def user_exists(username):
    """检查用户是否已存在"""
    url = f"{SUPABASE_URL}/rest/v1/users?username=eq.{username}&select=id"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    return resp.status_code == 200 and len(resp.json()) > 0


def insert_user(user_data):
    """插入用户（密码自动 bcrypt 哈希）"""
    hashed = bcrypt.hashpw(
        user_data['password'].encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    payload = {
        'username': user_data['username'],
        'email': user_data['email'],
        'password': hashed,
        'role': user_data['role'],
        'phone': user_data.get('phone', '')
    }
    url = f"{SUPABASE_URL}/rest/v1/users"
    resp = requests.post(url, json=payload, headers=HEADERS, timeout=10)
    return resp


def main():
    print("=" * 50)
    print("慧眼识癌 - Supabase 种子数据插入")
    print(f"目标: {SUPABASE_URL}")
    print("=" * 50)

    for user in SEED_USERS:
        name = user['username']
        if user_exists(name):
            print(f"⏭️  用户 '{name}' 已存在，跳过")
            continue

        resp = insert_user(user)
        if resp.status_code in (200, 201):
            print(f"✅ 用户 '{name}' (角色: {user['role']}) 插入成功")
        else:
            print(f"❌ 用户 '{name}' 插入失败: {resp.status_code} - {resp.text[:200]}")

    # 显示当前所有用户
    print("\n--- 当前 users 表 ---")
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/users?select=id,username,email,role,created_at&order=id",
        headers=HEADERS, timeout=10
    )
    if resp.status_code == 200:
        for u in resp.json():
            print(f"  [{u['id']}] {u['username']} | {u['email']} | {u['role']} | {u.get('created_at','')}")
    else:
        print(f"  查询失败: {resp.status_code}")


if __name__ == '__main__':
    main()
