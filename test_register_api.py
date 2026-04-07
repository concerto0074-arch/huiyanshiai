import requests
import json
import sys

url = 'http://127.0.0.1:5000/api/register'
data = {
    'username': 'testuser_' + str(hash(str(__file__)) % 10000),
    'email': f'test{hash(str(__file__)) % 10000}@test.com',
    'password': 'password123'
}

print('Testing register API...')
print(f'URL: {url}')
print(f'Data: {json.dumps(data, indent=2)}')

try:
    resp = requests.post(url, json=data, timeout=30)
    print(f'\nStatus Code: {resp.status_code}')
    print(f'Response Headers: {dict(resp.headers)}')
    print(f'Response Body: {resp.text}')
    
    if resp.status_code == 200:
        result = resp.json()
        if result.get('success'):
            print('\n✅ SUCCESS: User registered!')
            print(f"User ID: {result['user']['id']}")
        else:
            print(f'\n❌ FAILED: {result.get("error")}')
    elif resp.status_code == 500:
        print('\n❌ INTERNAL SERVER ERROR (500)')
        print('Backend has an error. Check backend.log')
    else:
        print(f'\n⚠️ Unexpected status: {resp.status_code}')
        
except requests.exceptions.ConnectionError as e:
    print(f'\n❌ Connection Error: Backend not running?')
    print(f'Details: {e}')
except requests.exceptions.Timeout:
    print('\n❌ Timeout: Backend not responding')
except Exception as e:
    print(f'\n❌ Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
