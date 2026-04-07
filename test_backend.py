import sys
import os

# 设置路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))

print('Starting backend test...')
print(f'Python path: {sys.path}')
print(f'Current dir: {os.getcwd()}')

try:
    print('Importing app...')
    from app import app
    print('✓ App imported successfully')
    
    print('Importing config...')
    from config import MODELS_DIR
    print(f'✓ Config loaded, models dir: {MODELS_DIR}')
    
    # 测试环境变量
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(env_path)
    
    supabase_url = os.getenv('SUPABASE_URL')
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    jwt_secret = os.getenv('JWT_SECRET')
    
    print(f'SUPABASE_URL: {supabase_url[:30]}...' if supabase_url else 'NOT SET')
    print(f'SUPABASE_ANON_KEY: {anon_key[:20]}...' if anon_key else 'NOT SET')
    print(f'JWT_SECRET: {jwt_secret[:20]}...' if jwt_secret else 'NOT SET')
    
except Exception as e:
    print(f'✗ Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
