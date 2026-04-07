import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('d:\\huiyanshiai(2.0)\\.env')

url = os.environ.get('DATABASE_URL')
print('Testing connection to', url)
try:
    conn = psycopg2.connect(url)
    print('Connection successful')
    conn.close()
except Exception as e:
    print('Error:', e)
