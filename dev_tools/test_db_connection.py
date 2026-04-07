"""数据库连接诊断脚本"""
import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('d:\\huiyanshiai(2.0)\\.env')

print("=" * 60)
print("数据库连接诊断")
print("=" * 60)

# 检查环境变量
supabase_url = os.getenv('SUPABASE_URL')
anon_key = os.getenv('SUPABASE_ANON_KEY')

print(f"\n1. 环境变量检查:")
print(f"   SUPABASE_URL: {supabase_url}")
print(f"   SUPABASE_ANON_KEY 长度: {len(anon_key) if anon_key else 0}")
print(f"   SUPABASE_ANON_KEY 前20字符: {anon_key[:20] if anon_key else 'None'}...")
print(f"   SUPABASE_ANON_KEY 后20字符: ...{anon_key[-20:] if anon_key else 'None'}")

# 标准 Supabase anon key 格式检查
if anon_key and anon_key.startswith('eyJ'):
    print(f"   ✅ Key 格式正确 (JWT 格式)")
else:
    print(f"   ❌ Key 格式错误 (应该是 eyJ 开头的 JWT)")

# 测试 REST API
print(f"\n2. REST API 连接测试:")
headers = {
    "apikey": anon_key,
    "Authorization": f"Bearer {anon_key}",
    "Content-Type": "application/json"
}

# 测试基本连接
try:
    response = requests.get(f"{supabase_url}/rest/v1/", headers=headers, timeout=10)
    print(f"   REST API 根路径状态码: {response.status_code}")
except Exception as e:
    print(f"   ❌ 连接失败: {e}")

# 测试 users 表
try:
    response = requests.get(f"{supabase_url}/rest/v1/users?select=id,username,email,role", headers=headers, timeout=10)
    print(f"   users 表查询状态码: {response.status_code}")
    if response.status_code == 200:
        users = response.json()
        print(f"   ✅ 成功获取 {len(users)} 个用户")
        for u in users:
            print(f"      - {u.get('username')} ({u.get('role', 'user')})")
    else:
        print(f"   ❌ 查询失败: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ 请求异常: {e}")

# 测试 patients 表
try:
    response = requests.get(f"{supabase_url}/rest/v1/patients?select=id&limit=1", headers=headers, timeout=10)
    print(f"   patients 表查询状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ patients 表可访问")
    else:
        print(f"   ⚠️ patients 表可能不存在或无权限: {response.text[:100]}")
except Exception as e:
    print(f"   ❌ 请求异常: {e}")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
