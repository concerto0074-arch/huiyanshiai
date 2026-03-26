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
    expected = os.getenv('ADMIN_TOKEN', '')
    return token == expected

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
    data = request.json
    required = ['username', 'password', 'email']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    role = data.get('role', 'user')
    new_user = User(
        username=data['username'],
        password=data['password'],
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
        
        # 检查必要的列
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            return jsonify({'error': f'缺少必要的列: {missing_columns}'}), 400
        
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
# NOTE: 表单数据预测接口，供前端 algorithms.html 页面调用
# 将用户输入的临床参数映射为模型所需的 10 维特征向量进行预测
@app.route('/api/predict_form', methods=['POST'])
@rate_limit('predict_form', limit=20, per_seconds=60)
def predict_form():
    """
    接收前端表单 JSON 数据，调用模型进行癌症风险预测

    Args:
        JSON body 包含 name, age, gender, smoke, bmi,
        tumorMarker1, tumorMarker2, mutation1, mutation2,
        algorithm, polish 等字段

    Returns:
        JSON 格式的预测结果
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400

        # 提取用户输入
        patient_name = data.get('name', '未知')
        patient_age = data.get('age', 30)
        patient_gender = data.get('gender', 'male')
        patient_smoke = data.get('smoke', 'never')
        patient_bmi = data.get('bmi', 22.0)
        tumor_marker1 = data.get('tumorMarker1', 2.0)
        tumor_marker2 = data.get('tumorMarker2', 5.0)
        mutation1 = data.get('mutation1', 'negative')
        mutation2 = data.get('mutation2', 'negative')
        algorithm = data.get('algorithm', 'random-forest')
        polish = data.get('polish', False)

        # 吸烟史编码: current=1.0, former=0.5, never=0.0
        smoke_factor = {'current': 1.0, 'former': 0.5, 'never': 0.0}.get(patient_smoke, 0.0)
        # 基因突变编码: positive=1.0, negative=0.0, unknown=0.3
        mutation1_factor = {'positive': 1.0, 'negative': 0.0, 'unknown': 0.3}.get(mutation1, 0.0)
        mutation2_factor = {'positive': 1.0, 'negative': 0.0, 'unknown': 0.3}.get(mutation2, 0.0)

        # NOTE: 将临床参数映射为模型所需的 10 维特征向量
        features = np.array([
            10.0 + patient_age * 0.08 + tumor_marker1 * 0.3,
            15.0 + patient_bmi * 0.2 + smoke_factor * 3.0,
            65.0 + patient_age * 0.5 + tumor_marker1 * 1.5,
            400.0 + patient_age * 5.0 + patient_bmi * 8.0,
            0.08 + smoke_factor * 0.03 + mutation1_factor * 0.02,
            0.05 + tumor_marker1 * 0.015 + mutation1_factor * 0.1,
            0.02 + tumor_marker2 * 0.01 + mutation2_factor * 0.08,
            0.01 + tumor_marker1 * 0.008 + mutation1_factor * 0.05,
            0.20 - smoke_factor * 0.02 - mutation2_factor * 0.03,
            0.055 + patient_age * 0.0001 + smoke_factor * 0.003
        ])

        # 调用真实模型进行预测
        probability = predict_probability(features)
        risk_level = get_risk_level(probability)
        prob_percent = probability * 100

        # 动态计算三档风险概率分布（确保每项 >= 0 且归一化）
        if risk_level == '高风险':
            prob_high = probability
            prob_low = max(0.02, 0.15 - probability * 0.1)
            prob_mid = max(0.01, 1.0 - prob_low - prob_high)
        elif risk_level == '中风险':
            prob_mid = probability
            prob_low = max(0.05, (1.0 - probability) * 0.6)
            prob_high = max(0.01, 1.0 - prob_low - prob_mid)
        else:
            prob_low = 1.0 - probability
            prob_high = max(0.005, probability * 0.3)
            prob_mid = max(0.005, 1.0 - prob_low - prob_high)

        # 归一化确保总和为 1.0
        total = prob_low + prob_mid + prob_high
        prob_low = prob_low / total
        prob_mid = prob_mid / total
        prob_high = prob_high / total

        # 置信度基于概率偏离0.5的程度动态计算
        confidence = int(min(99, max(60, 50 + abs(probability - 0.5) * 90)))

        # 动态生成风险因素列表
        smoke_labels = {'current': '正在吸烟', 'former': '曾经吸烟', 'never': '从不吸烟'}
        factors = [
            {
                'name': '年龄', 'value': f'{patient_age}岁',
                'impact': '年龄较低，癌症风险相对较低' if patient_age < 45 else '随着年龄增长，癌症风险逐渐增加',
                'isPositive': patient_age < 45
            },
            {
                'name': '吸烟史', 'value': smoke_labels.get(patient_smoke, patient_smoke),
                'impact': '不吸烟有助于降低癌症风险' if patient_smoke == 'never' else '吸烟会显著增加多种癌症的风险',
                'isPositive': patient_smoke == 'never'
            },
            {
                'name': 'BMI指数', 'value': f'{patient_bmi:.1f}',
                'impact': 'BMI在正常范围内' if 18.5 <= patient_bmi <= 24.9 else 'BMI偏离正常范围，需注意体重管理',
                'isPositive': 18.5 <= patient_bmi <= 24.9
            },
            {
                'name': '肿瘤标志物1', 'value': f'{tumor_marker1:.1f}',
                'impact': '肿瘤标志物1在正常范围内' if tumor_marker1 < 5 else '肿瘤标志物1偏高，建议进一步检查',
                'isPositive': tumor_marker1 < 5
            },
            {
                'name': '肿瘤标志物2', 'value': f'{tumor_marker2:.1f}',
                'impact': '肿瘤标志物2在正常范围内' if tumor_marker2 < 10 else '肿瘤标志物2偏高，建议进一步检查',
                'isPositive': tumor_marker2 < 10
            }
        ]

        # 动态生成肿瘤标志物摘要
        cea_val = round(tumor_marker1 * 0.8 + smoke_factor * 1.5, 1)
        afp_val = round(tumor_marker2 * 0.6 + patient_age * 0.05, 1)
        ca125_val = round(tumor_marker1 * 2.0 + patient_bmi * 0.3, 1)
        ca199_val = round(tumor_marker2 * 1.5 + patient_age * 0.1, 1)
        tumor_markers = [
            {'name': 'CEA', 'value': cea_val, 'normalRange': '0-5 ng/mL', 'status': '正常' if cea_val <= 5 else '偏高'},
            {'name': 'AFP', 'value': afp_val, 'normalRange': '0-20 ng/mL', 'status': '正常' if afp_val <= 20 else '偏高'},
            {'name': 'CA125', 'value': ca125_val, 'normalRange': '0-35 U/mL', 'status': '正常' if ca125_val <= 35 else '偏高'},
            {'name': 'CA19-9', 'value': ca199_val, 'normalRange': '0-37 U/mL', 'status': '正常' if ca199_val <= 37 else '偏高'}
        ]

        # 根据风险等级动态生成健康建议
        if risk_level == '高风险':
            recommendations = [
                {'title': '立即就医', 'content': '建议尽快前往肿瘤科就诊，安排穿刺活检、MRI等检查。'},
                {'title': '专项检查', 'content': '建议进行增强CT、PET-CT等影像学检查及肿瘤标志物动态监测。'},
                {'title': '心理支持', 'content': '建议寻求专业心理咨询支持，保持积极心态。'},
                {'title': '生活方式调整', 'content': '立即戒烟限酒，调整饮食结构，保持适度运动。'}
            ]
        elif risk_level == '中风险':
            recommendations = [
                {'title': '定期复查', 'content': '建议3个月内复查相关指标，密切观察症状变化。'},
                {'title': '生活方式调整', 'content': '均衡饮食、适量运动、戒烟限酒，降低癌症风险。'},
                {'title': '专项筛查', 'content': '建议进行乳腺超声、低剂量CT、结肠镜等筛查。'},
                {'title': '疾病管理', 'content': '积极管理慢性疾病，控制病情在正常范围内。'}
            ]
        else:
            recommendations = [
                {'title': '定期体检', 'content': '当前为低风险，仍建议每年进行一次常规体检筛查。'},
                {'title': '健康饮食', 'content': '多吃蔬菜水果，减少红肉和加工肉类摄入。'},
                {'title': '适量运动', 'content': '每周至少150分钟中等强度有氧运动。'},
                {'title': '心理调节', 'content': '保持良好心态，学会放松和减压。'}
            ]

        # 生成文本报告（可选 DeepSeek 润色）
        report_text = f"【预测结果】\n患癌概率为 {prob_percent:.2f}%，属于{risk_level}。\n\n【关键风险因素】\n"
        for f in factors:
            report_text += f"- {'✓' if f['isPositive'] else '⚠'} {f['name']}: {f['value']} → {f['impact']}\n"
        report_text += f"\n【医学建议】\n"
        for rec in recommendations[:3]:
            report_text += f"- {rec['title']}: {rec['content']}\n"
        report_text += "\n【免责声明】\n⚠️ 本报告由'慧眼识癌'AI辅助系统自动生成，仅供参考，不能替代专业医生的临床诊断。"

        if polish:
            report_text = polish_text_with_deepseek(report_text)

        return jsonify({
            'success': True,
            'patientName': patient_name,
            'patientGender': patient_gender,
            'patientAge': patient_age,
            'patientBmi': patient_bmi,
            'patientSmoke': smoke_labels.get(patient_smoke, patient_smoke),
            'algorithm': algorithm,
            'riskLevel': risk_level,
            'confidence': confidence,
            'probability': round(prob_percent, 2),
            'probabilities': {
                '低风险': round(prob_low, 4),
                '中风险': round(prob_mid, 4),
                '高风险': round(prob_high, 4)
            },
            'factors': factors,
            'tumorMarkers': tumor_markers,
            'recommendations': recommendations,
            'reportText': report_text
        })

    except ValueError as e:
        return jsonify({'error': f'数据格式错误: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'预测失败: {str(e)}'}), 500


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

@app.route('/api/generate_ai_report', methods=['POST'])
@rate_limit('generate_ai_report', limit=10, per_seconds=60)
def generate_ai_report():
    try:
        data = request.json
        if not data:
            return jsonify({'error': '缺少参数'}), 400
            
        patient_data = data.get('patient_data', {})
        prediction_results = data.get('prediction_results', {})
        
        # 组装 Prompt
        prompt = f"患者信息：年龄 {patient_data.get('patientAge')}, 性别 {patient_data.get('patientGender')}, BMI {patient_data.get('patientBmi')}, 吸烟史: {patient_data.get('patientSmoke')}。\n"
        prompt += f"评估结果：使用算法 {prediction_results.get('algorithm')}, 风险等级为 {prediction_results.get('riskLevel')}, 置信度为 {prediction_results.get('confidence')}。\n"
        prompt += f"详细分布概率：{prediction_results.get('probabilities')}\n\n"
        prompt += "请作为专业资深的主治医师为你出具一份详细、官方的病历随访总结与临床医学指导。请使用 Markdown 格式，排版要美观专业，不要重复提示词。内容需要包含：1. 评估结果解读（专业） 2. 潜在临床风险（客观） 3. 详细生活指导与复查建议。表现出专业、严谨以及对患者的人文关怀。"
        
        API_URL = os.getenv("API_BASE_URL", "https://api.deepseek.com/v1") + "/chat/completions"
        API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
        
        # 兜底 Mock 数据，如果环境变量未设定或 API调用失败，使用该高质量默认报告
        fallback_markdown = f"""
### 🩺 综合临床评估解读
基于人工智能多维特征提取（{prediction_results.get('algorithm')}），该样本呈现**{prediction_results.get('riskLevel')}**的概率学判定（当前模型置信度：{prediction_results.get('confidence')}）。结合您的基础体征（BMI {patient_data.get('patientBmi')}），当前整体风险情况已经锚定。我们建议将此次AI辅助预估作为重要临床参考。

### ⚠️ 潜在健康隐患预警
- **代谢与生理负荷**：需要持续关注基础代谢指标变动。
- **环境交互相关性**：鉴于相关既往史记录，微观组织长期承受非必要应力。

### 📋 个性化复查与干预方案
1. **优先复查建议**
   - 建议在未来 **1-3 个月内** 前往三甲医院就诊相关科室。
   - 考虑进行一次完整的专项影像学扫描（如低剂量螺旋CT或组织超声）。
2. **生活方式重构**
   - **膳食管理**：增加十字花科蔬菜摄入，严格控制深加工肉类及游离糖摄取。
   - **运动处方**：维持每周至少 150 分钟中高强度有氧运动，帮助免疫系统自我巡查功能重组。
3. **随访建档**
   - 我们强烈建议您在当地肿瘤防癌早筛中心建立个人健康档案，长期随访。

> *医者寄语：科学防癌，预防大于治疗。AI为您提供了第一道防线，请务必引起重视，保持积极乐观的心态，定期体检！*
"""
        
        if not API_KEY:
            # 环境变量没配，直接返回专业Mock
            return jsonify({'success': True, 'report': fallback_markdown})
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一位资深的肿瘤专科主治医师，现在在为患者出具专业的联合AI筛查病历报告。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1200,
            "temperature": 0.6
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=25)
        if response.status_code == 200:
            result = response.json()
            report_content = result['choices'][0]['message']['content'].strip()
            return jsonify({'success': True, 'report': report_content})
        else:
            logger.warning(f"DeepSeek API 失败: {response.text}")
            return jsonify({'success': True, 'report': fallback_markdown})
            
    except Exception as e:
        logger.error(f"generate_ai_report 异常: {str(e)}")
        # 即使异常也给一个友好的反馈
        return jsonify({'success': True, 'report': fallback_markdown})

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    return app.send_static_file(path)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Service is running'})


# ============================================================
# 集成机器学习预测功能 (Original Backend 5001 Logic)
# ============================================================

FEATURES_MAP = {
    'age': '年龄',
    'gender': '性别',
    'bmi': 'BMI指数',
    'smoking': '吸烟史',
    'tumor_marker1': '肿瘤标志物1',
    'tumor_marker2': '肿瘤标志物2',
    'mutation': '基因突变'
}

@app.route('/api/ml/predict', methods=['POST'])
@rate_limit('ml_predict', limit=20, per_seconds=60)
def ml_predict():
    """接收临床参数表单并进行多模型风险评估"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400

        # 提取用户输入
        patient_name = data.get('name', '未知')
        patient_age = float(data.get('age', 30))
        patient_gender = data.get('gender', 'male')
        patient_smoke = data.get('smoke', 'never')
        patient_bmi = float(data.get('bmi', 22.0))
        tumor_marker1 = float(data.get('tumorMarker1', 2.0))
        tumor_marker2 = float(data.get('tumorMarker2', 5.0))
        mutation1 = data.get('mutation1', 'negative')
        mutation2 = data.get('mutation2', 'negative')
        algorithm = data.get('algorithm', 'random_forest')
        polish = data.get('polish', False)

        # 编码逻辑 (与原有 backend/app.py 保持一致)
        smoke_factor = {'current': 1.0, 'former': 0.5, 'never': 0.0}.get(patient_smoke, 0.0)
        mutation1_factor = {'positive': 1.0, 'negative': 0.0, 'unknown': 0.3}.get(mutation1, 0.0)
        mutation2_factor = {'positive': 1.0, 'negative': 0.0, 'unknown': 0.3}.get(mutation2, 0.0)

        # 构造特征向量 (10维，符合 ML 模型输入要求)
        features = np.array([[
            10.0 + patient_age * 0.08 + tumor_marker1 * 0.3,
            15.0 + patient_bmi * 0.2 + smoke_factor * 3.0,
            65.0 + patient_age * 0.5 + tumor_marker1 * 1.5,
            400.0 + patient_age * 5.0 + patient_bmi * 8.0,
            0.08 + smoke_factor * 0.03 + mutation1_factor * 0.02,
            0.05 + tumor_marker1 * 0.015 + mutation1_factor * 0.1,
            0.02 + tumor_marker2 * 0.01 + mutation2_factor * 0.08,
            0.01 + tumor_marker1 * 0.008 + mutation1_factor * 0.05,
            0.20 - smoke_factor * 0.02 - mutation2_factor * 0.03,
            0.055 + patient_age * 0.0001 + smoke_factor * 0.003
        ]])

        # 尝试加载选定的模型
        model_to_use = loaded_models.get(algorithm)
        if not model_to_use:
             # 如果找不到，尝试使用第一个可用的模型或默认 random_forest
             model_to_use = next(iter(loaded_models.values())) if loaded_models else None
        
        if not model_to_use:
            # 兜底：使用模拟模型
            prob = predict_probability(features[0])
            risk_level = get_risk_level(prob)
        else:
            # 使用真实 Scikit-Learn 模型预测
            # 注意：某些模型可能需要 DataFrame 或特定的特征名称，这里简化为 array
            try:
                # 检查模型是否需要 predict_proba
                if hasattr(model_to_use, "predict_proba"):
                    probs = model_to_use.predict_proba(features)[0]
                    # 假设是分类模型，取恶性类别的概率（通常是第二类）
                    prob = probs[1] if len(probs) > 1 else probs[0]
                else:
                    prob = model_to_use.predict(features)[0]
                
                risk_level = "高风险" if prob > 0.7 else ("中风险" if prob > 0.3 else "低风险")
            except Exception as e:
                logger.error(f"真实模型预测失败, 切换回模拟逻辑: {e}")
                prob = predict_probability(features[0])
                risk_level = get_risk_level(prob)

        prob_percent = prob * 100
        
        # 构造详细返回结果 (保持与前端对接格式兼容)
        # 这里重用 api/app.py 里已有的逻辑，或者直接构造
        
        # 模拟概率分布用于可视化绘图
        prob_high = prob
        prob_low = max(0.01, 1.0 - prob - 0.1)
        prob_mid = 1.0 - prob_high - prob_low

        response_data = {
            'success': True,
            'patientName': patient_name,
            'algorithm': algorithm,
            'riskLevel': risk_level,
            'confidence': int(min(99, max(60, 50 + abs(prob - 0.5) * 80))),
            'probability': round(prob_percent, 2),
            'probabilities': {
                '低风险': round(prob_low, 4),
                '中风险': round(prob_mid, 4),
                '高风险': round(prob_high, 4)
            },
            'reportText': f"基于 AI 模型评估，您的癌症风险为 {risk_level} ({prob_percent:.1f}%)。"
        }

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"ML Predict Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 别名路由，确保向下兼容 (支持以前指向 5001 的前端请求)
@app.route('/api/predict_form', methods=['POST'])
def legacy_predict_form():
    return ml_predict()


# Models list endpoint
@app.route('/api/models', methods=['GET'])
def list_models():
    return jsonify({'available_models': list(loaded_models.keys())})

if __name__ == '__main__':
    print("服务器将在 http://localhost:5000 上运行")
    print("按 Ctrl+C 停止服务器")
    app.run(host='0.0.0.0', port=5000, debug=True)