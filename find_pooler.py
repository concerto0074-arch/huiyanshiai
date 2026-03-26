import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('d:\\huiyanshiai(2.0)\\.env')

project_ref = 'cfwsuuygpxkiayntyajt'
password = 'zsy2044348092'

# Top regions for Chinese users: Tokyo, Singapore, Seoul, Hong Kong, US West
regions = [
    'ap-northeast-1',  # Tokyo
    'ap-southeast-1',  # Singapore
    'ap-northeast-2',  # Seoul
    'ap-east-1',       # Hong Kong
    'us-west-1',       # N. California
    'us-west-2',       # Oregon
    'us-east-1',       # N. Virginia
    'eu-central-1',    # Frankfurt
    'eu-west-1',       # Ireland
    'eu-west-2',       # London
    'ca-central-1',    # Canada
    'sa-east-1',       # Sao Paulo
    'ap-south-1',      # Mumbai
    'ap-southeast-2',  # Sydney
]

print('Hunting for the correct Supabase pooler URL...')

success_url = None

for region in regions:
    url = f'postgresql://postgres.{project_ref}:{password}@aws-0-{region}.pooler.supabase.com:6543/postgres'
    try:
        conn = psycopg2.connect(url, connect_timeout=3)
        print(f'SUCCESS! Connected to region: {region}')
        success_url = url
        conn.close()
        break
    except Exception as e:
        # print(f'Failed {region}')
        pass

if success_url:
    print('FOUND_URL:', success_url)
    
    # Update .env
    with open('d:\\huiyanshiai(2.0)\\.env', 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    import re
    new_content = re.sub(r'DATABASE_URL=.*', f'DATABASE_URL={success_url}', env_content)
    
    with open('d:\\huiyanshiai(2.0)\\.env', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('.env updated successfully with the working pooler URL.')
else:
    print('Could not find the correct region or password is wrong.')
