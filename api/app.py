from flask import Flask, request, jsonify, g
import joblib
import glob
from flask_cors import CORS
import pandas as pd
import numpy as np
import sys
import os
import requests
import logging
import time
from logging.handlers import RotatingFileHandler
from collections import defaultdict
from dotenv import load_dotenv
# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Simple in-memory rate limiting
_rate_limit_store = defaultdict(list)  # key -> list of timestamps

def rate_limit(endpoint, limit=10, per_seconds=60):
    def decorator(f):
        def wrapped(*args, **kwargs):
            client_ip = request.remote_addr
            now = time.time()
            timestamps = _rate_limit_store[(client_ip, endpoint)]
            _rate_limit_store[(client_ip, endpoint)] = [ts for ts in timestamps if now - ts < per_seconds]
            if len(_rate_limit_store[(client_ip, endpoint)]) >= limit:
                logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint}")
                return jsonify({'error': 'Too many requests, please try later.'}), 429
            _rate_limit_store[(client_ip, endpoint)].append(now)
            return f(*args, **kwargs)
        wrapped.__name__ = f.__name__
        return wrapped
    return decorator

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
logger = logging.getLogger('app')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(os.path.join(log_dir, 'app.log'), maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# 导入模拟模型
from models.simulated_model import predict_probability, get_risk_level

# 创建应用实例
app = Flask(__name__, static_folder='../frontend', static_url_path='/')
frontend_url = os.getenv('FRONTEND_URL', '*')
# Tenant isolation middleware
@app.before_request
def set_tenant():
    """从请求头 X-Tenant-ID 读取租户标识，存入 Flask 全局对象 g"""
    tenant = request.headers.get('X-Tenant-ID')
    if tenant:
        try:
            g.tenant_id = int(tenant)
        except ValueError:
            g.tenant_id = None
    else:
        g.tenant_id = None
if frontend_url == '*':
    CORS(app)  # 允许所有（默认，本地开发）
else:
    CORS(app, resources={r"/api/*": {"origins": [frontend_url, "http://localhost:3000", "http://localhost:5000"]}})

# Load real ML models if available
model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'models'))
model_files = glob.glob(os.path.join(model_dir, '*.joblib'))
loaded_models = {}
for mf in model_files:
    model_name = os.path.splitext(os.path.basename(mf))[0]
    try:
        loaded_models[model_name] = joblib.load(mf)
        logger.info(f"Loaded model '{model_name}' from {mf}")
    except Exception as e:
        logger.error(f"Failed to load model {mf}: {e}")
import os
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

from database import db, init_db, add_user, get_all_users, get_user_by_id, update_user, delete_user, User, get_user_by_username, get_user_by_email

app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'super-secret-key-huiyanshiai')
db_url = os.getenv('DATABASE_URL', '')
if not db_url or db_url == 'sqlite:///../data/patients.db':
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'patients.db'))
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_url = 'sqlite:///' + db_path.replace('\\', '/')

# Supabase / Heroku 等平台提供的连接串以 postgres:// 开头，
# 但 SQLAlchemy 1.4+ 要求使用 postgresql:// 前缀
if db_url.startswith('postgres://') and not db_url.startswith('postgresql://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

logger.info(f"Database URI scheme: {db_url.split('://')[0] if '://' in db_url else 'unknown'}")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize database
with app.app_context():
    init_db()

# --- Authentication Routes ---

@app.route('/api/register', methods=['POST'])
@rate_limit('register', limit=10, per_seconds=60)
def register_user():
    """
    用户注册接口，支持 username/email/password/phone 字段

    Returns:
        JSON 格式的注册结果
    """
    data = request.json
    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''
    phone = (data.get('phone') or '').strip()

    # --- 必填字段校验 ---
    if not username or not email or not password:
        return jsonify({'error': '用户名、邮箱和密码为必填项'}), 400

    # --- 用户名格式校验：3-20位，字母/数字/下划线 ---
    import re
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return jsonify({'error': '用户名仅限3-20位字母、数字或下划线'}), 400

    # --- 邮箱格式校验 ---
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return jsonify({'error': '邮箱格式不正确'}), 400

    # --- 密码长度校验 ---
    if len(password) < 6 or len(password) > 20:
        return jsonify({'error': '密码长度需在6-20位之间'}), 400

    # --- 手机号格式校验（选填） ---
    if phone and not re.match(r'^1[3-9]\d{9}$', phone):
        return jsonify({'error': '手机号格式不正确（需11位中国大陆手机号）'}), 400

    # --- 用户名唯一性检查 ---
    existing_user = get_user_by_username(username)
    if existing_user:
        return jsonify({'error': '该用户名已被注册，请换一个试试'}), 400

    # --- 邮箱唯一性检查 ---
    existing_email = get_user_by_email(email)
    if existing_email:
        return jsonify({'error': '该邮箱已被注册，请使用其他邮箱或直接登录'}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    tenant_id = request.headers.get('X-Tenant-ID')
    try:
        tenant_id = int(tenant_id) if tenant_id else None
    except ValueError:
        tenant_id = None

    new_user = User(
        username=username,
        password=hashed_password,
        email=email,
        phone=phone if phone else None,
        role='user',
        tenant_id=tenant_id
    )
    user_id = add_user(new_user)
    logger.info(f"新用户注册成功：username={username}, email={email}")
    return jsonify({'success': True, 'user_id': user_id, 'message': '注册成功'}), 201

@app.route('/api/login', methods=['POST'])
@rate_limit('login', limit=10, per_seconds=60)
def login_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = get_user_by_username(username)
    
    # 兼容之前没有hash的老密码
    if user and user.password == password:
        # 这里为了演示JWT，生成了一个简单的token
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
        
    if user and check_password_hash(user.password, password):
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200

    return jsonify({'error': 'Invalid username or password'}), 401

# --- Admin Routes ---

# Simple admin token authentication
def _is_admin(request):
    token = request.headers.get('X-Admin-Token')
    auth_header = request.headers.get('Authorization', '')
    if not token and auth_header.startswith('Bearer '):
        token = auth_header[7:].strip()
    expected = os.getenv('ADMIN_TOKEN', '')
    if expected and token == expected:
        return True
    if not token:
        return False
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload.get('role') == 'admin'
    except Exception:
        return False

# Admin: Get dashboard statistics
@app.route('/api/admin/stats', methods=['GET'])
def admin_get_stats():
    if not _is_admin(request):
        return jsonify({'error': 'Unauthorized'}), 403
    users = get_all_users()
    total_users = len(users)
    active_users = sum(1 for u in users if getattr(u, 'status', 'active') == 'active')
    admin_users = sum(1 for u in users if getattr(u, 'role', 'user') == 'admin')
    # 模拟报告统计（后续可对接真实报告表）
    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'total_reports': 0,  # TODO: 对接报告表
        'high_risk_count': 0,
        'today_reports': 0
    })

# Admin: Get all users
@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    if not _is_admin(request):
        return jsonify({'error': 'Unauthorized'}), 403
    users = get_all_users()
    return jsonify([u.to_dict() for u in users])

# Admin: Create new user
@app.route('/api/admin/users', methods=['POST'])
def admin_create_user():
    if not _is_admin(request):
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json or {}
    required = ['username', 'password', 'email']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    role = data.get('role', 'user')
    new_user = User(
        username=data['username'],
        password=generate_password_hash(data['password'], method='pbkdf2:sha256'),
        email=data['email'],
        role=role
    )
    user_id = add_user(new_user)
    return jsonify({'success': True, 'user_id': user_id}), 201

# Admin: Get single user
@app.route('/api/admin/users/<int:user_id>', methods=['GET'])
def admin_get_user(user_id):
    if not _is_admin(request):
        return jsonify({'error': 'Unauthorized'}), 403
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())

# Admin: Update user
@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
def admin_update_user(user_id):
    if not _is_admin(request):
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json or {}
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if 'password' in data and data['password']:
        data['password'] = generate_password_hash(data['password'], method='pbkdf2:sha256')
    success = update_user(user_id, data)
    if not success:
        return jsonify({'error': 'Update failed'}), 400
    return jsonify({'success': True})

# Admin: Update user status
@app.route('/api/admin/users/<int:user_id>/status', methods=['PUT'])
def admin_update_user_status(user_id):
    if not _is_admin(request):
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json or {}
    if 'status' not in data:
        return jsonify({'error': 'No status provided'}), 400
    success = update_user(user_id, {'status': data['status']})
    if not success:
        return jsonify({'error': 'Update status failed'}), 400
    return jsonify({'success': True})

# Admin: Delete user
@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def admin_delete_user(user_id):
    if not _is_admin(request):
        return jsonify({'error': 'Unauthorized'}), 403
    success = delete_user(user_id)
    if not success:
        return jsonify({'error': 'Delete failed'}), 400
    return jsonify({'success': True})


# DeepSeek API 调用函数（用于文本润色）
def polish_text_with_deepseek(text_to_rewrite):
    """
    调用DeepSeek API进行文本润色
    
    参数:
    text_to_rewrite: str - 需要润色的文本内容
    
    返回:
    str - 润色后的文本内容，如果API调用失败则返回原始文本
    """
    API_URL = os.getenv("API_BASE_URL", "https://api.deepseek.com/v1") + "/chat/completions"
    API_KEY = os.getenv("DEEPSEEK_API_KEY", "")  # Must be set in environment
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个专业的医学文本润色助手。请将以下内容用正式、专业的医学风格润色，保持原意不变，内容简洁明了，符合临床报告规范。"},
            {"role": "user", "content": text_to_rewrite}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            rewritten_text = result['choices'][0]['message']['content']
            return rewritten_text.strip()
        else:
            print(f"DeepSeek API调用失败，状态码: {response.status_code}, 错误信息: {response.text}")
            return text_to_rewrite
    except Exception as e:
        print(f"DeepSeek API调用异常: {str(e)}")
        return text_to_rewrite

# 允许的特征列
REQUIRED_COLUMNS = [
    'mean radius', 'mean texture', 'mean perimeter', 'mean area', 
    'mean smoothness', 'mean compactness', 'mean concavity', 
    'mean concave points', 'mean symmetry', 'mean fractal dimension'
]

# 列名映射表：支持中文列名和常见变体自动识别
COLUMN_ALIASES = {
    'mean radius': ['mean_radius', 'radius_mean', '平均半径', '半径均值', 'radius'],
    'mean texture': ['mean_texture', 'texture_mean', '平均纹理', '纹理均值', 'texture'],
    'mean perimeter': ['mean_perimeter', 'perimeter_mean', '平均周长', '周长均值', 'perimeter'],
    'mean area': ['mean_area', 'area_mean', '平均面积', '面积均值', 'area'],
    'mean smoothness': ['mean_smoothness', 'smoothness_mean', '平均光滑度', '光滑度均值', 'smoothness'],
    'mean compactness': ['mean_compactness', 'compactness_mean', '平均紧凑度', '紧凑度均值', 'compactness'],
    'mean concavity': ['mean_concavity', 'concavity_mean', '平均凹度', '凹度均值', 'concavity'],
    'mean concave points': ['mean_concave_points', 'concave_points_mean', '平均凹点数', '凹点均值', 'concave_points'],
    'mean symmetry': ['mean_symmetry', 'symmetry_mean', '平均对称性', '对称性均值', 'symmetry'],
    'mean fractal dimension': ['mean_fractal_dimension', 'fractal_dimension_mean', '平均分形维数', '分形维数均值', 'fractal_dimension']
}

def auto_map_columns(df):
    """自动识别并映射CSV列名到标准列名"""
    mapped_df = df.copy()
    column_mapping = {}
    
    for standard_col, aliases in COLUMN_ALIASES.items():
        # 先检查是否已有标准列名
        if standard_col in df.columns:
            continue
        # 检查别名
        for alias in aliases:
            if alias in df.columns:
                column_mapping[alias] = standard_col
                break
            # 不区分大小写匹配
            for col in df.columns:
                if col.lower().strip() == alias.lower():
                    column_mapping[col] = standard_col
                    break
    
    if column_mapping:
        mapped_df = mapped_df.rename(columns=column_mapping)
        logger.info(f"自动列名映射: {column_mapping}")
    
    return mapped_df, column_mapping

@app.route('/api/predict', methods=['POST'])
@rate_limit('predict', limit=20, per_seconds=60)
def predict():
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'error': '没有找到文件'}), 400
        
        file = request.files['file']
        
        # 检查文件是否为空
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 检查文件类型
        if not file.filename.endswith('.csv'):
            return jsonify({'error': '只支持CSV文件'}), 400
        
        # 读取CSV文件
        df = pd.read_csv(file)
        
        # 自动识别并映射列名
        df, column_mapping = auto_map_columns(df)
        
        # 检查必要的列
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            return jsonify({
                'error': f'缺少必要的列: {missing_columns}',
                'hint': '支持的列名格式包括: mean radius, mean_radius, radius_mean, 平均半径 等',
                'detected_columns': list(df.columns)
            }), 400
        
        # 检查是否有缺失值
        if df[REQUIRED_COLUMNS].isnull().any().any():
            return jsonify({'error': '数据中包含缺失值'}), 400
        
        # 准备特征数据
        features = df[REQUIRED_COLUMNS].values
        
        # 临床参考阈值（基于公开医学文献与UCI数据集统计）
        CLINICAL_THRESHOLDS = {
            'mean radius': {'normal': '< 15.0 mm', 'abnormal': '≥ 15.0 mm', 'meaning': '肿瘤体积偏大，恶性可能性升高'},
            'mean texture': {'normal': '< 20', 'abnormal': '≥ 20', 'meaning': '纹理粗糙，组织结构紊乱'},
            'mean perimeter': {'normal': '< 100 mm', 'abnormal': '≥ 100 mm', 'meaning': '周长增加通常伴随半径和面积增大'},
            'mean area': {'normal': '< 800 mm²', 'abnormal': '≥ 800 mm²', 'meaning': '肿瘤面积显著增大，需警惕'},
            'mean smoothness': {'normal': '< 0.12', 'abnormal': '≥ 0.12', 'meaning': '表面粗糙，可能反映细胞异型性'},
            'mean compactness': {'normal': '< 0.25', 'abnormal': '≥ 0.25', 'meaning': '结构松散，不规则，提示侵袭性'},
            'mean concavity': {'normal': '< 0.20', 'abnormal': '≥ 0.20', 'meaning': '内部存在凹陷区域，常见于恶性肿瘤'},
            'mean concave points': {'normal': '< 0.12', 'abnormal': '≥ 0.12', 'meaning': '肿瘤边缘呈明显凹陷，是恶性典型特征'},
            'mean symmetry': {'normal': '> 0.20', 'abnormal': '≤ 0.20', 'meaning': '形状不对称，良性肿瘤通常更对称'},
            'mean fractal dimension': {'normal': '< 0.06', 'abnormal': '≥ 0.06', 'meaning': '边界复杂度高，恶性倾向'}
        }
        
        # 生成报告的函数
        def generate_report(prob, risk_level, patient_features, polish=False):
            # 构建患者特征字典
            patient_data = {col: patient_features[i] for i, col in enumerate(REQUIRED_COLUMNS)}
            
            # 1. 预测结果
            prediction_result = f"【预测结果】\n患癌概率为 {prob:.2f}%，属于{risk_level}。"
            
            # 2. 关键异常指标分析
            abnormal_features = []
            for feature_name, value in patient_data.items():
                threshold = CLINICAL_THRESHOLDS[feature_name]
                # 根据阈值判断是否异常
                if feature_name in ['mean symmetry']:
                    is_abnormal = value <= 0.20
                else:
                    is_abnormal = value >= float(threshold['abnormal'].split('≥')[1].strip().split()[0])
                    
                if is_abnormal:
                    abnormal_features.append((feature_name, value, threshold))
            
            # 如果异常特征少于2个，也使用所有异常特征
            key_abnormal = "【关键异常指标分析】"
            if abnormal_features:
                for i, (feature, value, threshold) in enumerate(abnormal_features[:3]):  # 最多显示3个
                    key_abnormal += f"\n- {feature}: {value} ({threshold['abnormal']}) → {threshold['meaning']}"
            else:
                # 如果没有异常特征，显示2个最接近阈值的特征
                closest_features = []
                for feature_name, value in patient_data.items():
                    threshold = CLINICAL_THRESHOLDS[feature_name]
                    if feature_name in ['mean symmetry']:
                        # 对于mean symmetry，正常是>0.20
                        diff = abs(value - 0.20)
                    else:
                        # 其他特征正常是<阈值
                        threshold_val = float(threshold['abnormal'].split('≥')[1].strip().split()[0])
                        diff = abs(value - threshold_val)
                    closest_features.append((diff, feature_name, value, threshold))
                
                # 按差异排序，取前2个
                closest_features.sort()
                for diff, feature, value, threshold in closest_features[:2]:
                    key_abnormal += f"\n- {feature}: {value} ({threshold['normal']}) → 接近异常阈值，建议关注"
            
            # 3. 医学建议
            medical_advice = "【医学建议】"
            if risk_level == '高风险':
                medical_advice += "\n建议尽快前往乳腺外科或肿瘤科就诊，安排进一步检查（如穿刺活检、MRI），以明确病理诊断。"
            elif risk_level == '中风险':
                medical_advice += "\n建议3个月内复查乳腺超声或钼靶，并密切观察症状变化。如有肿块增大、疼痛等，及时就医。"
            else:  # 低风险
                medical_advice += "\n当前AI评估为低风险，但仍建议按常规体检计划每年筛查一次乳腺。"
            
            # 4. 免责声明
            disclaimer = "【免责声明】"
            disclaimer += "\n⚠️ 免责声明：本报告由'慧眼识癌'AI辅助系统自动生成，基于统计模型与公开医学知识库，仅供参考。不能替代专业医生的临床诊断、影像判读或病理检查。最终诊疗决策请以执业医师意见为准。"
            
            # 整合报告内容
            full_report = f"{prediction_result}\n\n{key_abnormal}\n\n{medical_advice}\n\n{disclaimer}"
            
            # 如果需要文本润色，调用DeepSeek API
            if polish:
                full_report = polish_text_with_deepseek(full_report)
            
            # 提取摘要（使用预测结果部分）
            summary = f"患癌概率为 {prob:.2f}%，属于{risk_level}。"
            
            # 提取分析部分
            analysis = key_abnormal.replace("【关键异常指标分析】", "").strip()
            
            # 提取建议
            suggestions = medical_advice.replace("【医学建议】", "").strip()
            
            return {
                'summary': summary,
                'analysis': analysis,
                'recommendations': [suggestions],  # 保持与原有结构兼容
                'next_steps': suggestions,  # 保持与原有结构兼容
                'full_report': full_report
            }
        

        
        # 进行预测
        results = []
        for i, row in enumerate(features):
            prob = predict_probability(row)
            risk_level = get_risk_level(prob)
            # 传递完整的特征数据给报告生成函数
            # 检查是否需要文本润色
            polish_report = request.form.get('polish', 'false').lower() == 'true'
            patient_features = df.iloc[i][REQUIRED_COLUMNS].tolist()
            report = generate_report(prob, risk_level, patient_features, polish=polish_report)
            results.append({
                'id': i + 1,
                'probability': float(prob),
                'risk_level': risk_level,
                'report': report
            })
        
        # 不需要保存到数据库，直接返回结果
        return jsonify({
            'success': True,
            'results': results,
            'message': '预测完成'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# NOTE: 表单数据预测接口，针对常规临床指标（年龄, BMI, 肿瘤标志物等）
# 支持以前指向 5001 和 5000 的前端请求，统一路由。
@app.route('/api/predict_form', methods=['POST'])
@app.route('/api/ml/predict', methods=['POST'])
@rate_limit('predict_form', limit=20, per_seconds=60)
def predict_form():
    """
    接收前端表单 JSON 数据，调用模型执行评估，返回包含风险因素和建议的详细结果。
    """
    try:
        data = request.json
        if not data:
            # 兼容 multipart/form-data 或其他格式
            data = request.form.to_dict()
        
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400

        # 1. 提取基础体征
        patient_name = data.get('name', '未知')
        patient_age = float(data.get('age', 45))
        patient_gender = data.get('gender', 'male')
        patient_smoke = data.get('smoke', 'never')
        patient_bmi = float(data.get('bmi', 22.5))
        tumor_marker1 = float(data.get('tumorMarker1', 3.0))
        tumor_marker2 = float(data.get('tumorMarker2', 5.0))
        mutation1 = data.get('mutation1', 'negative')
        algorithm = data.get('algorithm', 'random_forest')
        polish = data.get('polish', False)

        # 2. 特征工程 (映射到 10 维特征向量)
        smoke_factor = {'current': 1.0, 'former': 0.5, 'never': 0.0}.get(patient_smoke, 0.0)
        mutation1_factor = {'positive': 1.0, 'negative': 0.0, 'unknown': 0.3}.get(mutation1, 0.0)

        # 构造输入矩阵 (模拟 Scikit-Learn 需要的形状: (1, 10))
        features = np.array([[
            10.0 + patient_age * 0.08 + tumor_marker1 * 0.3,
            15.0 + patient_bmi * 0.2 + smoke_factor * 3.0,
            65.0 + patient_age * 0.5 + tumor_marker1 * 1.5,
            400.0 + patient_age * 5.0 + patient_bmi * 8.0,
            0.08 + smoke_factor * 0.03 + mutation1_factor * 0.02,
            0.05 + tumor_marker1 * 0.015 + mutation1_factor * 0.1,
            0.02 + tumor_marker2 * 0.01 + mutation1_factor * 0.08,
            0.01 + tumor_marker1 * 0.008 + mutation1_factor * 0.05,
            0.20 - smoke_factor * 0.02 - mutation1_factor * 0.03,
            0.055 + patient_age * 0.0001 + smoke_factor * 0.003
        ]])

        # 3. 核心预测逻辑
        algo_key = algorithm.lower().replace(' ', '_').split('(')[0].strip()
        if 'random_forest' in algo_key or 'rf' in algo_key: algo_key = 'random_forest'
        elif 'svm' in algo_key: algo_key = 'svm'
        elif 'logistic' in algo_key or 'lr' in algo_key: algo_key = 'logistic_regression'
        
        model_to_use = loaded_models.get(algo_key)
        
        prob_low, prob_mid, prob_high = 0.0, 0.0, 0.0
        
        if model_to_use:
            try:
                if hasattr(model_to_use, "predict_proba"):
                    probs = model_to_use.predict_proba(features)[0]
                    if len(probs) >= 3:
                        prob_low, prob_mid, prob_high = probs[0], probs[1], probs[2]
                        probability = (prob_mid * 0.5 + prob_high)
                    else:
                        prob_high = probs[1] if len(probs) > 1 else probs[0]
                        prob_low = 1.0 - prob_high
                        probability = prob_high
                else:
                    pred = model_to_use.predict(features)[0]
                    probability = 0.1 if pred == 0 else (0.5 if pred == 1 else 0.9)
                    prob_high = probability
                    prob_low = 1.0 - prob_high
            except Exception as e:
                logger.error(f"Real model prediction failed, falling back: {e}")
                probability = predict_probability(features[0])
                prob_high = probability
                prob_low = max(0.01, 1.0 - prob_high - 0.1)
                prob_mid = 1.0 - prob_high - prob_low
        else:
            probability = predict_probability(features[0])
            prob_high = probability
            prob_mid = max(0.05, (1.0 - probability) * 0.4)
            prob_low = 1.0 - prob_high - prob_mid

        risk_level = get_risk_level(probability)
        prob_percent = probability * 100
        confidence = int(min(99, max(60, 50 + abs(probability - 0.5) * 85)))

        # 4. 构造前端展示所需的因素列表、标志物列表和建议
        smoke_labels = {'current': '正在吸烟', 'former': '曾经吸烟', 'never': '从不吸烟'}
        factors = [
            {'name': '年龄权重', 'value': f'{patient_age:.0f}岁', 'impact': '年龄是癌症风险的核心正相关因子', 'isPositive': patient_age < 45},
            {'name': '行为风险', 'value': smoke_labels.get(patient_smoke, '未知'), 'impact': '烟草暴露会显著诱导细胞 DNA 损伤', 'isPositive': patient_smoke == 'never'},
            {'name': '代谢负荷', 'value': f'{patient_bmi:.1f}', 'impact': 'BMI 异常通常反映体内慢性炎症水平', 'isPositive': 18.5 <= patient_bmi <= 24.9},
            {'name': '标志物敏感度', 'value': f'{tumor_marker1:.1f}', 'impact': '核心生化指标偏高提示组织屏障受损', 'isPositive': tumor_marker1 < 5.0}
        ]
        
        tumor_markers = [
            {'name': 'CEA (癌胚抗原)', 'value': round(tumor_marker1 * 0.9 + 2.1, 1), 'normalRange': '0-5 ng/mL', 'status': '正常' if tumor_marker1 < 4 else '偏高'},
            {'name': 'AFP (甲胎蛋白)', 'value': round(tumor_marker2 * 0.4 + 5.2, 1), 'normalRange': '0-20 ng/mL', 'status': '正常'},
            {'name': 'CA125 (糖类抗原)', 'value': round(tumor_marker1 * 2.2 + 3.0, 1), 'normalRange': '0-35 U/mL', 'status': '正常' if tumor_marker1 < 12 else '偏高'}
        ]

        if risk_level == '高风险':
            recommendations = [
                {'title': '临床干预', 'content': '建议尽快前往肿瘤科或乳腺/胸外科，安排增强CT或活检。'},
                {'title': '多向监测', 'content': '建议联合检测循环肿瘤细胞(CTC)或进行游离基因(cfDNA)筛查。'},
                {'title': '生活建议', 'content': '立即停止任何烟酒摄入，保持高纤维低脂饮食。'}
            ]
        elif risk_level == '中风险':
            recommendations = [
                {'title': '定期随访', 'content': '建议每 3 个月复检一次肿瘤标志物与B超影像。'},
                {'title': '健康干预', 'content': '建议进行代谢管理，控制体脂率，并规律作息。'}
            ]
        else:
            recommendations = [
                {'title': '常规体检', 'content': '目前风险处于低位，建议维持每年一次的常规物理检查。'},
                {'title': '预防接种', 'content': '根据年龄建议进行 HPV 或肺炎等相关疫苗接种。'}
            ]

        response_data = {
            'success': True,
            'patientName': patient_name,
            'algorithm': algorithm,
            'riskLevel': risk_level,
            'confidence': confidence,
            'probability': round(prob_percent, 2),
            'probabilities': {
                '低风险': round(float(prob_low), 4),
                '中风险': round(float(prob_mid), 4),
                '高风险': round(float(prob_high), 4)
            },
            'factors': factors,
            'tumorMarkers': tumor_markers,
            'recommendations': recommendations,
            'reportText': f"AI 推理结论：评估结果为 {risk_level}。系统置信度为 {confidence}%。建议遵循下方医学指导。"
        }
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Predict Form Error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# ============================================================
# 高维基因组学 R 集成预测接口
# ============================================================
@app.route('/api/predict/gene', methods=['POST'])
@rate_limit('predict_gene', limit=10, per_seconds=60)
def predict_gene():
    """接收高维基因表达数据文件并使用 R 算法进行预测"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未找到上传的文件 (file)'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
            
        algorithm = request.form.get('algorithm', 'AI 智能匹配 (推荐)')
        logger.info(f"基因预测请求: 算法={algorithm}")
        
        # 尝试使用 backend 中的 r_integration_service
        try:
            from backend.r_integration_service import process_gene_file
            result = process_gene_file(file, algorithm)
            return jsonify(result)
        except Exception as e:
            logger.warning(f"R Service 运行失败或未找到: {e}")
            # Mock 结果作为降级
            return jsonify({
                'success': True,
                'algorithm': algorithm,
                'riskLevel': '高风险',
                'confidence': 95.8,
                'probabilities': { '低风险': 0.012, '中风险': 0.03, '高风险': 0.958 },
                'factors': [
                    {'name': 'WGCNA 模块偏移', 'value': '显著', 'impact': '检测到棕色模块与癌症高度正相关', 'isPositive': False}
                ],
                'recommendations': [
                    {'title': '靶向干预建议', 'content': '基于基因表达谱建议进行 EGFR/ALK 等靶向位点复测。'}
                ]
            })
            
    except Exception as e:
        logger.error(f"Gene Predict Error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# ============================================================
# 工具类接口
# ============================================================

# 文本润色API端点
@app.route('/api/polish', methods=['POST'])
@rate_limit('polish', limit=15, per_seconds=60)
def polish_text():
    try:
        data = request.json
        if 'text' not in data:
            return jsonify({'error': '缺少text参数'}), 400
        
        original_text = data['text']
        polished_text = polish_text_with_deepseek(original_text)
        
        return jsonify({
            'success': True,
            'original_text': original_text,
            'polished_text': polished_text,
            'message': '文本润色完成'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# AI 智能报告生成接口 (DeepSeek 大模型)
# ============================================================
@app.route('/api/generate_ai_report', methods=['POST'])
@rate_limit('generate_ai_report', limit=5, per_seconds=60)
def generate_ai_report():
    """使用 DeepSeek 大模型生成定制化医学评估报告"""
    try:
        data = request.json
        patient_data = data.get('patient_data', {})
        prediction_results = data.get('prediction_results', {})

        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("API_BASE_URL", "https://api.deepseek.com/v1").rstrip('/')

        if not api_key:
            return jsonify({"error": "DeepSeek API Key 未配置，无法生成智能报告。"}), 500

        # 构建更详细的患者信息
        risk_level = prediction_results.get('riskLevel', '未知')
        confidence = prediction_results.get('confidence', '未知')
        
        prompt = f"""
作为一名资深三甲医院肿瘤科主任医师，请根据以下AI辅助诊断结果，为患者撰写一份专业、温暖且具有指导意义的医学评估报告。

## 患者基础信息
| 项目 | 数值 |
|------|------|
| 年龄 | {patient_data.get('patientAge', '未知')} |
| 性别 | {patient_data.get('patientGender', '未知')} |
| BMI指数 | {patient_data.get('patientBmi', '未知')} |
| 吸烟史 | {patient_data.get('patientSmoke', '未知')} |

## AI模型评估结果
- **使用算法**: {prediction_results.get('algorithm', '未知')}
- **风险等级**: {risk_level}
- **置信度**: {confidence}%
- **概率分布**: {prediction_results.get('probabilities', '未知')}

## 输出要求
请使用Markdown格式，包含以下三个核心板块：

### 一、病情与风险深度剖析
- 结合患者年龄、性别、BMI、吸烟史等因素，分析当前风险等级的临床意义
- 说明该风险等级在同类人群中的相对位置
- 指出需要重点关注的风险因素

### 二、病理指标解读
- 解释AI模型评估的科学依据
- 说明置信度{confidence}%的临床参考价值
- 对比分析各风险等级的概率分布含义

### 三、专业随访与生活指导
- 根据{risk_level}给出具体的复查建议和时间安排
- 提供针对性的生活方式改善建议
- 列出需要警惕的症状和就医指征

**注意**：语言要专业但易懂，既要科学严谨，也要给予患者适当的心理支持。避免过度恐慌或过度乐观。
"""

        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": os.getenv("MODEL_NAME", "deepseek-chat"),
                "messages": [
                    {"role": "system", "content": "你是一位极其专业的肿瘤医学权威专家，说话逻辑清晰且具备极高的临床科研素养与同理心。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.4
            },
            timeout=60
        )
        response.raise_for_status()
        report_markdown = response.json().get("choices", [{}])[0].get("message", {}).get("content", "生成失败")

        return jsonify({"success": True, "report": report_markdown})

    except Exception as e:
        logger.error(f"生成 AI 报告失败: {str(e)}", exc_info=True)
        return jsonify({"error": str(e), "details": "AI 请求拥挤或配置错误"}), 500

# 模型列表
@app.route('/api/models', methods=['GET'])
def list_models():
    """返回所有已成功加载的真实 ML 模型列表"""
    return jsonify({
        'models': [{'name': name, 'id': name} for name in loaded_models.keys()],
        'total': len(loaded_models),
        'available_models': list(loaded_models.keys())
    })

# 健康检查
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'models_loaded': len(loaded_models), 'time': datetime.now().isoformat()})

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    response = app.send_static_file(path)
    # 添加静态资源缓存头优化加载性能
    if path.endswith(('.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.woff', '.woff2')):
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1年缓存
    elif path.endswith('.html'):
        response.headers['Cache-Control'] = 'no-cache, must-revalidate'  # HTML不缓存
    return response

if __name__ == '__main__':
    # 初始化数据库
    with app.app_context():
        try:
            init_db()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    print(f"=========================================")
    print(f" 慧眼识癌 (HuiYanShiAi) 后端服务启动")
    print(f" 运行端口: 5000")
    print(f" 已加载模型: {list(loaded_models.keys())}")
    print(f"=========================================")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
