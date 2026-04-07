import requests
import json

# 测试注册 API
url = 'http://127.0.0.1:5000/api/register'
data = {
    'username': 'testuser888',
    'email': 'test888@example.com',
    'password': 'password123'
}

print('Testing register API...')
try:
    resp = requests.post(url, json=data, timeout=15)
    print(f'Status: {resp.status_code}')
    result = resp.json()
    print(f'Response: {json.dumps(result, ensure_ascii=False, indent=2)}')
    if result.get('success'):
        print('\n✅ SUCCESS: User registered and saved to database')
        print(f'User ID: {result["user"]["id"]}')
    else:
        print(f'\n❌ FAILED: {result.get("error")}')
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
