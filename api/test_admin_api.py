import requests, json, time

base = 'http://127.0.0.1:5000/api/admin/users'
headers = {'X-Admin-Token': 'admin-secret-token'}

# Wait for server to start
time.sleep(1)

# GET list
r = requests.get(base, headers=headers)
print('GET status', r.status_code)
print('GET body', r.text[:200])

# POST new user
payload = {'username': 'testuser', 'password': 'testpass', 'email': 'test@example.com'}
r2 = requests.post(base, json=payload, headers=headers)
print('POST status', r2.status_code)
print('POST body', r2.text)

# GET again
r3 = requests.get(base, headers=headers)
print('GET after POST status', r3.status_code)
print('GET after POST body', r3.text[:200])
