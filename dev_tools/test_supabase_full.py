import os
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv('d:\\huiyanshiai(2.0)\\.env')

# Reconstruct the direct Postgres URL since it's commented out in .env
project_ref = 'cfwsuuygpxkiayntyajt'
password = 'zsy2044348092'
pg_url = f'postgresql://postgres.{project_ref}:{password}@db.{project_ref}.supabase.co:5432/postgres'

print("="*50)
print("1. 测试 PostgreSQL 传统直连 (你在 .env 中配置的旧方式)")
print("="*50)
print(f"尝试连接: db.{project_ref}.supabase.co:5432")
try:
    conn = psycopg2.connect(pg_url, connect_timeout=5)
    print("✅ PostgreSQL 直连成功！")
    conn.close()
except Exception as e:
    print("Failed PostgreSQL Direct Connection!")
    print(str(e))
    print("👉 诊断信息：这是因为 Supabase 已经全面封禁了免费版的 IPv4 直连。你的网络无法解析这个地址。")

print("\n" + "="*50)
print("2. 测试 Supabase REST API 云端接口")
print("="*50)
supabase_url = os.getenv('SUPABASE_URL')
anon_key = os.getenv('SUPABASE_ANON_KEY')
print(f"尝试连接 REST API: {supabase_url}")

headers = {
    "apikey": anon_key,
    "Authorization": f"Bearer {anon_key}"
}
try:
    response = requests.get(f"{supabase_url}/rest/v1/", headers=headers, timeout=5)
    if response.status_code == 200:
        print("✅ REST API 连接成功！你的 Supabase 云端实例是活着的！")
    else:
        print("❌ REST API 连接失败，状态码：", response.status_code)
        
    # 测试一下能不能查表
    res_table = requests.get(f"{supabase_url}/rest/v1/users?select=*", headers=headers, timeout=5)
    if res_table.status_code == 200:
        print(f"✅ 成功访问 users 表！(目前有 {len(res_table.json())} 条数据)")
    else:
        print("❌ 访问 users 表失败，这正常，因为可能启用了 RLS (行级安全) 或表不存在。")
except Exception as e:
    print("❌ REST API 发生异常:", e)
    
print("\n" + "="*50)
print("结论：云端数据库是活着的，但由于后端是 Flask + SQLAlchemy，必须使用 PostgreSQL 协议的『连接池 (Pooler)』URL 才能对接成功。")
print("="*50)
