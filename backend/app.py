from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import os
import json
import logging
import datetime
import urllib.parse
from functools import wraps
import requests
import bcrypt
import jwt
from dotenv import load_dotenv

# 加载 .env 环境变量
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')

from config import (
    MODELS_DIR, MODEL_SUFFIX, RESULTS_FILE, 
    FEATURES, model_descriptions, API_HOST, API_PORT, API_DEBUG
)
from utils import (
    load_model, load_results, ensure_dir, setup_logging,
    map_smoking_status, map_gender, map_mutation
)
from r_integration_service import process_gene_file


# 设置日志
logger = setup_logging()

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
CORS(app, origins=[
    "http://127.0.0.1:5000",
    "http://localhost:5000",
    "https://huiyanshiai.zsypioneer.cn",
    "*"
])  # 允许跨域：本地5000端口 + 生产域名


@app.after_request
def add_cache_headers(resp):
    try:
        path = request.path or ''

        # Never cache API responses
        if path.startswith('/api/'):
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp

        # Never cache HTML (avoid stale pages / auth state)
        if path == '/' or path.endswith('.html') or path == '':
            resp.headers['Cache-Control'] = 'no-cache'
            return resp

        # JS/CSS: no cache (dev mode)
        if any(path.endswith(ext) for ext in ('.js', '.css')):
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
            return resp

        # Cache other static assets (images/fonts)
        if any(path.endswith(ext) for ext in (
            '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico',
            '.woff', '.woff2', '.ttf', '.eot'
        )):
            resp.headers['Cache-Control'] = 'public, max-age=2592000, immutable'
            return resp
    except Exception:
        return resp

    return resp

# 初始化全局变量
models = {}
model_info = {}
model_results = {}

# 移除 init_models，改为直接在文件级别加载（或仅在 __main__ 及需要时加载）
# 这里我们直接调用 load_models() 以确保所有 worker 都能加载它，或者交给 WSGI 容器加载
with app.app_context():
    pass # 如果需要的话

def get_runtime_status():
    supabase_url = os.getenv('SUPABASE_URL')
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    jwt_secret = os.getenv('JWT_SECRET')

    status = {
        'backend': 'ok',
        'models_loaded': len(models),
        'models': list(models.keys()),
        'supabase_configured': bool(supabase_url and anon_key),
        'supabase_reachable': False,
        'jwt_configured': bool(jwt_secret)
    }

    if supabase_url and anon_key:
        try:
            resp = requests.get(
                f"{supabase_url}/rest/v1/",
                headers={
                    'apikey': anon_key,
                    'Authorization': f'Bearer {anon_key}'
                },
                timeout=5
            )
            status['supabase_reachable'] = resp.status_code < 500
        except Exception:
            status['supabase_reachable'] = False

    return status

def load_models():
    """加载所有模型"""
    global models, model_info, model_results
    
    logger.info(f"从{MODELS_DIR}加载模型...")
    
    # 获取所有模型文件
    model_files = [f for f in os.listdir(MODELS_DIR) if f.endswith(MODEL_SUFFIX)]
    
    for model_file in model_files:
        model_name = model_file.replace(MODEL_SUFFIX, '')
        model_path = os.path.join(MODELS_DIR, model_file)
        
        try:
            models[model_name] = load_model(model_path)
            logger.info(f"成功加载模型: {model_name}")
            
            # 设置模型信息
            model_info[model_name] = {
                'name': model_name,
                'description': model_descriptions.get(model_name, f'{model_name}算法'),
                'features': list(FEATURES.keys()),
                'feature_names': list(FEATURES.values())
            }
        except Exception as e:
            logger.error(f"加载模型{model_name}失败: {str(e)}")
    
    # 加载训练结果
    try:
        results_path = os.path.join(MODELS_DIR, RESULTS_FILE)
        if os.path.exists(results_path):
            model_results = load_results(results_path)
            logger.info("成功加载训练结果")
    except Exception as e:
        logger.error(f"加载训练结果失败: {str(e)}")
    
    logger.info(f"共加载{len(models)}个模型: {list(models.keys())}")

# 初始化加载模型，这样不论是被 gunicorn 导入还是 python 直接运行都能加载到
load_models()

# NOTE: 不在模块级别调用 load_models()，避免 Flask/Werkzeug 双重导入时覆盖全局变量

@app.route('/api/models', methods=['GET'])
def get_models():
    """获取所有可用模型"""
    logger.info(f"[API] 查询可用模型，当前字典大小: {len(models)}, keys: {list(models.keys())}")
    return jsonify({
        'models': list(model_info.values()),
        'total': len(models)
    })

@app.route('/api/model/<model_name>', methods=['GET'])
def get_model_info(model_name):
    """获取单个模型的详细信息"""
    if model_name not in model_info:
        return jsonify({'error': f'模型{model_name}不存在'}), 404
    
    # 添加性能信息
    info = model_info[model_name].copy()
    if model_name in model_results:
        info['performance'] = {
            'cv_score': model_results[model_name].get('best_cv_score', 0),
            'test_accuracy': model_results[model_name].get('test_accuracy', 0),
            'best_params': model_results[model_name].get('best_params', {})
        }
    
    return jsonify(info)

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        # 获取请求数据
        data = request.json
        algorithm = data.get('algorithm', 'random_forest')
        patient_data = data.get('patient_data', {})
        
        logger.info(f"收到预测请求: 算法={algorithm}, 病人数据={patient_data}")
        
        # 验证算法类型
        if algorithm not in models:
            logger.error(f"不支持的算法: {algorithm}")
            return jsonify({'error': f'不支持的算法: {algorithm}'}), 400
        
        # 准备输入数据
        input_data = pd.DataFrame([{
            'age': patient_data.get('age', 0),
            'gender': 1 if patient_data.get('gender') == 'female' else 0,
            'bmi': patient_data.get('bmi', 0),
            'smoking': {'never': 0, 'former': 1, 'current': 2}.get(patient_data.get('smoke'), 0),
            'tumor_marker1': patient_data.get('tumorMarker1', 0),
            'tumor_marker2': patient_data.get('tumorMarker2', 0),
            'mutation': 1 if patient_data.get('mutation1') == 'positive' else 0
        }])
        
        logger.info(f"准备输入数据: {input_data.to_dict()}")
        
        # 加载模型并预测
        model = models[algorithm]
        prediction = model.predict(input_data)[0]
        probabilities = model.predict_proba(input_data)[0]
        
        logger.info(f"预测结果: 风险评分={prediction}, 概率分布={probabilities}")
        
        # 构建结果
        result = {
            'algorithm': algorithm,
            'risk_score': int(prediction),
            'risk_level': ['low', 'medium', 'high'][prediction],
            'confidence': float(max(probabilities) * 100),
            'probabilities': {
                'low': float(probabilities[0] * 100),
                'medium': float(probabilities[1] * 100),
                'high': float(probabilities[2] * 100)
            },
            'recommendations': [
                '保持健康的生活方式',
                '定期进行癌症筛查',
                '咨询专业医生'
            ],
            'patient_data': {
                'age': patient_data.get('age', 0),
                'gender': patient_data.get('gender', 'unknown'),
                'bmi': patient_data.get('bmi', 0),
                'smoke': patient_data.get('smoke', 'unknown'),
                'tumorMarker1': patient_data.get('tumorMarker1', 0),
                'tumorMarker2': patient_data.get('tumorMarker2', 0),
                'mutation1': patient_data.get('mutation1', 'unknown')
            }
        }
        
        logger.info(f"返回预测结果: {result}")
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"预测失败: {str(e)}", exc_info=True)
        return jsonify({'error': str(e), 'details': f'{type(e).__name__}: {str(e)}'}), 500

@app.route('/api/predict/test', methods=['GET'])
def test_predict():
    """测试预测功能"""
    # 测试样本数据
    test_sample = {
        'name': '测试病人',
        'age': 60,
        'gender': 'male',
        'smoke': 'current',
        'bmi': 28.5,
        'tumorMarker1': 150.5,
        'tumorMarker2': 60.2,
        'mutation1': 'positive'
    }
    
    # 使用随机森林模型进行预测
    test_data = {
        'algorithm': 'random_forest',
        'patient_data': test_sample
    }
    
    # 调用预测函数
    return predict_internal(test_data)

def predict_internal(data):
    """内部预测函数，供测试使用"""
    try:
        algorithm = data.get('algorithm', 'random_forest')
        patient_data = data.get('patient_data', {})
        
        if algorithm not in models:
            return jsonify({'error': f'不支持的算法: {algorithm}'}), 400
        
        # 准备输入数据
        input_data = pd.DataFrame([{
            'age': patient_data.get('age', 0),
            'gender': 1 if patient_data.get('gender') == 'female' else 0,
            'bmi': patient_data.get('bmi', 0),
            'smoking': {'never': 0, 'former': 1, 'current': 2}.get(patient_data.get('smoke'), 0),
            'tumor_marker1': patient_data.get('tumorMarker1', 0),
            'tumor_marker2': patient_data.get('tumorMarker2', 0),
            'mutation': 1 if patient_data.get('mutation1') == 'positive' else 0
        }])
        
        # 加载模型并预测
        model = models[algorithm]
        prediction = model.predict(input_data)[0]
        probabilities = model.predict_proba(input_data)[0]
        
        # 构建结果
        result = {
            'algorithm': algorithm,
            'risk_score': int(prediction),
            'risk_level': ['low', 'medium', 'high'][prediction],
            'confidence': float(max(probabilities) * 100),
            'probabilities': {
                'low': float(probabilities[0] * 100),
                'medium': float(probabilities[1] * 100),
                'high': float(probabilities[2] * 100)
            },
            'recommendations': [
                '保持健康的生活方式',
                '定期进行癌症筛查',
                '咨询专业医生'
            ]
        }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"内部预测失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict_form', methods=['POST'])
def predict_form():
    """前端表单预测接口 —— prediction_flow.js 调用此端点
    接收扁平化的患者数据，内部转发给 /api/predict 的核心逻辑，
    然后把结果翻译成前端 report.html 需要的中文格式返回。
    """
    try:
        data = request.json
        algorithm = data.get('algorithm', 'random_forest')
        patient_data = {
            'age': data.get('age', 0),
            'gender': data.get('gender', 'male'),
            'bmi': data.get('bmi', 22.5),
            'smoke': data.get('smoke', 'never'),
            'tumorMarker1': data.get('tumorMarker1', 0),
            'tumorMarker2': data.get('tumorMarker2', 0),
            'mutation1': data.get('mutation1', 'none')
        }

        logger.info(f"[predict_form] 算法={algorithm}, 患者={patient_data}")

        if algorithm not in models:
            # 降级到 random_forest
            algorithm = 'random_forest' if 'random_forest' in models else list(models.keys())[0] if models else None
            if not algorithm:
                return jsonify({'error': '没有可用的预测模型'}), 500

        input_data = pd.DataFrame([{
            'age': patient_data.get('age', 0),
            'gender': 1 if patient_data.get('gender') == 'female' else 0,
            'bmi': patient_data.get('bmi', 0),
            'smoking': {'never': 0, 'former': 1, 'current': 2}.get(patient_data.get('smoke'), 0),
            'tumor_marker1': patient_data.get('tumorMarker1', 0),
            'tumor_marker2': patient_data.get('tumorMarker2', 0),
            'mutation': 1 if patient_data.get('mutation1') == 'positive' else 0
        }])

        model = models[algorithm]
        prediction = model.predict(input_data)[0]
        probabilities = model.predict_proba(input_data)[0]

        risk_map = {0: '低风险', 1: '中风险', 2: '高风险'}
        risk_level = risk_map.get(int(prediction), '未知')
        conf = float(max(probabilities) * 100)

        age = patient_data.get('age', 0)
        cea = patient_data.get('tumorMarker1', 0)
        wbc = patient_data.get('tumorMarker2', 0)

        result = {
            'riskLevel': risk_level,
            'confidence': round(conf, 1),
            'probabilities': {
                '低风险': round(float(probabilities[0]), 4),
                '中风险': round(float(probabilities[1]), 4),
                '高风险': round(float(probabilities[2]), 4)
            },
            'factors': [
                {'name': '年龄', 'value': f'{age}岁', 'impact': '年龄是癌症风险的重要基线因素', 'isPositive': age < 50},
                {'name': '吸烟状态', 'value': patient_data.get('smoke', '未知'), 'impact': '长期吸烟显著增加多种癌症风险', 'isPositive': patient_data.get('smoke') == 'never'},
                {'name': 'BMI', 'value': str(patient_data.get('bmi', 0)), 'impact': 'BMI异常增加代谢相关癌症风险', 'isPositive': 18.5 <= float(patient_data.get('bmi', 22)) <= 25},
                {'name': '基因突变', 'value': patient_data.get('mutation1', '未知'), 'impact': '特定基因突变与肿瘤发生密切相关', 'isPositive': patient_data.get('mutation1') != 'positive'}
            ],
            'tumorMarkers': [
                {'name': 'CEA', 'value': cea, 'normalRange': '0-5 ng/mL', 'status': '正常' if float(cea) <= 5 else '偏高'},
                {'name': 'WBC', 'value': wbc, 'normalRange': '4-10 ×10⁹/L', 'status': '正常' if 4 <= float(wbc) <= 10 else '异常'}
            ],
            'recommendations': [
                {'title': '定期体检', 'content': '建议每年进行一次全面体检，包括肿瘤标志物检测。'},
                {'title': '生活方式', 'content': '保持均衡饮食、适量运动、戒烟限酒。'},
                {'title': '专科随访', 'content': '如有异常指标，建议到三甲医院肿瘤专科进一步评估。'}
            ],
            'patientName': '匿名用户'
        }

        logger.info(f"[predict_form] 预测完成: {risk_level}, 置信度={conf:.1f}%")
        return jsonify(result)

    except Exception as e:
        logger.error(f"predict_form 预测失败: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate_ai_report', methods=['POST'])
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
            
        prompt = f"""
请你作为一名资深三甲医院肿瘤科主任医师，根据以下患者的基础体征与最新的机器学习模型预测分析结果，直接撰写一份格式化、排版精美的临床医学建议。
切忌输出任何多余的客套话或废话。请全部使用Markdown格式，必须包含且清晰分为：【病情与风险深度剖析】、【病理指标解读】、【专业随访与生活指导】三个核心板块。

患者基础体征：
- 年龄：{patient_data.get('age')}
- 性别：{patient_data.get('gender')}
- BMI：{patient_data.get('bmi')}
- 吸烟史：{patient_data.get('smoke')}

AI模型算法评估系统（{prediction_results.get('algorithm')}）输出结果：
- 评定风险级别：{prediction_results.get('riskLevel')} (评估置信度：{prediction_results.get('confidence')}%)
- 量化抛物概率分布：{prediction_results.get('probabilities')}
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

@app.route('/api/predict/gene', methods=['POST'])
def predict_gene():
    """接收高维基因表达数据文件并使用 R 算法进行预测"""
    try:
        logger.info("收到高维基因数据预测请求 /api/predict/gene")
        if 'file' not in request.files:
            return jsonify({'error': '未找到上传的文件 (file)'}), 400
        
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'error': '未选择文件'}), 400

        algorithm = request.form.get('algorithm') or request.args.get('algorithm') or 'AI 智能匹配 (推荐)'
        logger.info(f"指定的基因分群算法: {algorithm}")
        
        # 将文件交给 R 集成服务处理
        result = process_gene_file(file, algorithm)
        
        logger.info(f"R 算法返回预测结果: {result['riskLevel']}")
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"基因预测失败: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    runtime_status = get_runtime_status()
    runtime_status['status'] = 'ok'
    runtime_status['timestamp'] = pd.Timestamp.now().isoformat()
    return jsonify(runtime_status)

@app.route('/api/system-status', methods=['GET'])
def system_status():
    runtime_status = get_runtime_status()
    runtime_status['timestamp'] = pd.Timestamp.now().isoformat()
    return jsonify(runtime_status)

@app.route('/', methods=['GET'])
def serve_frontend_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>', methods=['GET'])
def serve_frontend_assets(path):
    if path.startswith('api/'):
        return jsonify({'error': 'API route not found'}), 404
    target_path = os.path.join(FRONTEND_DIR, path)
    if os.path.isfile(target_path):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, 'index.html')

# ============================================================
# 登录功能（后端实现）
# ============================================================

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录接口，使用 Supabase REST API 验证用户名和密码（bcrypt 哈希校验）"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({'success': False, 'error': '缺少用户名或密码'}), 400

        supabase_url = os.getenv('SUPABASE_URL')
        anon_key = os.getenv('SUPABASE_ANON_KEY')
        if not supabase_url or not anon_key:
            logger.error('Supabase 配置缺失')
            return jsonify({'success': False, 'error': '服务器未配置 Supabase'}), 500

        # 先按用户名查出用户记录（包含哈希密码），再在后端做 bcrypt 校验
        query_url = f"{supabase_url}/rest/v1/users?username=eq.{username}&select=id,username,email,role,password,plan,status"
        headers = {
            'apikey': anon_key,
            'Authorization': f'Bearer {anon_key}',
            'Accept': 'application/json'
        }
        resp = requests.get(query_url, headers=headers, timeout=5)
        if resp.status_code != 200:
            logger.error(f'Supabase 查询失败，状态码 {resp.status_code}')
            return jsonify({'success': False, 'error': '登录验证失败'}), 500

        users = resp.json()
        if not users:
            return jsonify({'success': False, 'error': '用户名或密码错误'}), 401

        user = users[0]

        # 检查账户状态
        if user.get('status') in ('banned', 'inactive'):
            return jsonify({'success': False, 'error': '该账户已被禁用，请联系管理员'}), 403

        stored_hash = user.get('password', '')

        # 兼容旧的明文密码：如果不是 bcrypt 哈希则直接比较
        if stored_hash.startswith('$2b$') or stored_hash.startswith('$2a$'):
            if not bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                return jsonify({'success': False, 'error': '用户名或密码错误'}), 401
        else:
            if password != stored_hash:
                return jsonify({'success': False, 'error': '用户名或密码错误'}), 401

        # 生成 JWT Token
        jwt_secret = os.getenv('JWT_SECRET', 'huiyanshiai-default-secret-key')
        payload = {
            'user_id': user['id'],
            'username': user.get('username'),
            'role': user.get('role', 'user'),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, jwt_secret, algorithm='HS256')

        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user.get('username'),
                'email': user.get('email'),
                'role': user.get('role', 'user'),
                'plan': user.get('plan', 'free')
            },
            'token': token
        })
    except Exception as e:
        logger.error(f'登录异常: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500

# ============================================================
# 注册功能（后端实现）
# ============================================================

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册接口，向 Supabase 插入新用户记录（密码使用 bcrypt 哈希存储）"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone', '')
        plan = data.get('plan', 'free')  # free / standard / premium
        if not username or not email or not password:
            return jsonify({'success': False, 'error': '缺少必填字段'}), 400
        if len(password) < 8:
            return jsonify({'success': False, 'error': '密码长度至少8位'}), 400
        if plan not in ('free', 'standard', 'premium'):
            plan = 'free'

        supabase_url = os.getenv('SUPABASE_URL')
        anon_key = os.getenv('SUPABASE_ANON_KEY')
        if not supabase_url or not anon_key:
            logger.error('Supabase 配置缺失')
            return jsonify({'success': False, 'error': '服务器未配置 Supabase'}), 500

        # 先检查用户名或邮箱是否已存在（注意：用户名可能包含中文，必须做 URL 编码）
        username_q = urllib.parse.quote(str(username), safe='')
        email_q = urllib.parse.quote(str(email), safe='')
        check_url = f"{supabase_url}/rest/v1/users?or=(username.eq.{username_q},email.eq.{email_q})&select=id"
        check_headers = {
            'apikey': anon_key,
            'Authorization': f'Bearer {anon_key}',
            'Accept': 'application/json'
        }
        check_resp = requests.get(check_url, headers=check_headers, timeout=5)
        if check_resp.status_code == 200 and check_resp.json():
            return jsonify({'success': False, 'error': '用户名或邮箱已被注册'}), 409

        # 使用 bcrypt 对密码进行哈希
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        insert_url = f"{supabase_url}/rest/v1/users"
        headers = {
            'apikey': anon_key,
            'Authorization': f'Bearer {anon_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        payload = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'phone': phone,
            'role': 'user',
            'plan': plan
        }
        resp = requests.post(insert_url, json=payload, headers=headers, timeout=5)
        if resp.status_code not in (200, 201):
            logger.error(f'Supabase 注册失败，状态码 {resp.status_code}, 响应: {resp.text}')
            return jsonify({'success': False, 'error': '注册失败，请稍后重试'}), 500

        user = resp.json()[0] if isinstance(resp.json(), list) else resp.json()

        # 生成 JWT Token
        jwt_secret = os.getenv('JWT_SECRET', 'huiyanshiai-default-secret-key')
        payload_jwt = {
            'user_id': user.get('id'),
            'username': user.get('username'),
            'role': user.get('role', 'user'),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload_jwt, jwt_secret, algorithm='HS256')

        return jsonify({
            'success': True,
            'user': {
                'id': user.get('id'),
                'username': user.get('username'),
                'email': user.get('email'),
                'role': user.get('role', 'user'),
                'plan': user.get('plan', 'free')
            },
            'token': token
        })
    except Exception as e:
        logger.error(f'注册异常: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500


# ============================================================
# JWT 认证装饰器
# ============================================================

def token_required(f):
    """验证 JWT Token 的装饰器，解析后将 user payload 注入 request.user"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        if not token:
            return jsonify({'success': False, 'error': '缺少认证 Token'}), 401
        try:
            jwt_secret = os.getenv('JWT_SECRET', 'huiyanshiai-default-secret-key')
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': 'Token 已过期，请重新登录'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': '无效的 Token'}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """管理员权限装饰器，必须和 @token_required 一起使用（放在其后）"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.user.get('role') != 'admin':
            return jsonify({'success': False, 'error': '权限不足，仅管理员可访问'}), 403
        return f(*args, **kwargs)
    return decorated

def get_supabase_headers():
    """获取 Supabase REST API 通用请求头"""
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    return {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Prefer': 'return=representation'
    }

# ============================================================
# 普通用户 - 个人中心 API
# ============================================================

@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_user_profile():
    """获取当前登录用户的个人资料"""
    try:
        user_id = request.user.get('user_id')
        supabase_url = os.getenv('SUPABASE_URL')
        url = f"{supabase_url}/rest/v1/users?id=eq.{user_id}&select=id,username,email,phone,age,gender,role,status,plan,plan_expire_at,created_at"
        resp = requests.get(url, headers=get_supabase_headers(), timeout=5)
        if resp.status_code != 200 or not resp.json():
            return jsonify({'success': False, 'error': '用户不存在'}), 404
        user = resp.json()[0]
        return jsonify({'success': True, 'user': user})
    except Exception as e:
        logger.error(f'获取用户资料异常: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500

@app.route('/api/user/profile', methods=['PUT'])
@token_required
def update_user_profile():
    """更新当前登录用户的个人资料（用户名、邮箱、手机、年龄、性别）"""
    try:
        user_id = request.user.get('user_id')
        data = request.json
        supabase_url = os.getenv('SUPABASE_URL')

        allowed_fields = ['username', 'email', 'phone', 'age', 'gender']
        payload = {k: v for k, v in data.items() if k in allowed_fields and v is not None}
        if not payload:
            return jsonify({'success': False, 'error': '没有可更新的字段'}), 400

        url = f"{supabase_url}/rest/v1/users?id=eq.{user_id}"
        resp = requests.patch(url, json=payload, headers=get_supabase_headers(), timeout=5)
        if resp.status_code not in (200, 204):
            logger.error(f'更新用户资料失败: {resp.status_code} {resp.text}')
            return jsonify({'success': False, 'error': '更新失败'}), 500

        updated = resp.json()[0] if resp.json() else payload
        return jsonify({'success': True, 'user': updated})
    except Exception as e:
        logger.error(f'更新用户资料异常: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500

@app.route('/api/user/password', methods=['PUT'])
@token_required
def update_user_password():
    """修改当前登录用户的密码"""
    try:
        user_id = request.user.get('user_id')
        data = request.json
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')

        if not new_password or len(new_password) < 8:
            return jsonify({'success': False, 'error': '新密码长度至少8位，需包含字母和数字'}), 400

        supabase_url = os.getenv('SUPABASE_URL')
        # 先取出当前密码哈希
        url = f"{supabase_url}/rest/v1/users?id=eq.{user_id}&select=password"
        resp = requests.get(url, headers=get_supabase_headers(), timeout=5)
        if resp.status_code != 200 or not resp.json():
            return jsonify({'success': False, 'error': '用户不存在'}), 404

        stored_hash = resp.json()[0].get('password', '')
        # 校验旧密码
        if stored_hash.startswith('$2b$') or stored_hash.startswith('$2a$'):
            if not bcrypt.checkpw(old_password.encode('utf-8'), stored_hash.encode('utf-8')):
                return jsonify({'success': False, 'error': '当前密码错误'}), 401
        else:
            if old_password != stored_hash:
                return jsonify({'success': False, 'error': '当前密码错误'}), 401

        # 哈希新密码并更新
        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        update_url = f"{supabase_url}/rest/v1/users?id=eq.{user_id}"
        update_resp = requests.patch(update_url, json={'password': new_hash}, headers=get_supabase_headers(), timeout=5)
        if update_resp.status_code not in (200, 204):
            return jsonify({'success': False, 'error': '密码更新失败'}), 500

        return jsonify({'success': True, 'message': '密码修改成功'})
    except Exception as e:
        logger.error(f'修改密码异常: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500

@app.route('/api/user/reports', methods=['GET'])
@token_required
def get_user_reports():
    """获取当前登录用户的历史评估报告"""
    try:
        user_id = request.user.get('user_id')
        supabase_url = os.getenv('SUPABASE_URL')
        url = f"{supabase_url}/rest/v1/patients?user_id=eq.{user_id}&select=*&order=created_at.desc"
        resp = requests.get(url, headers=get_supabase_headers(), timeout=5)
        if resp.status_code != 200:
            return jsonify({'success': True, 'reports': []})
        return jsonify({'success': True, 'reports': resp.json()})
    except Exception as e:
        logger.error(f'获取用户报告异常: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500

@app.route('/api/save_report', methods=['POST'])
@token_required
def save_report():
    """将预测报告保存到 Supabase patients 表，关联当前登录用户"""
    try:
        user_id = request.user.get('user_id')
        data = request.json

        supabase_url = os.getenv('SUPABASE_URL')
        if not supabase_url:
            return jsonify({'success': False, 'error': '服务器未配置 Supabase'}), 500

        risk_level = data.get('riskLevel', '未知')
        confidence = data.get('confidence', 0)

        payload = {
            'user_id': user_id,
            'diagnosis': data.get('algorithm', '未知算法'),
            'probability': round(float(confidence) / 100, 4) if confidence else 0,
            'risk_level': risk_level,
            'summary': f"风险等级: {risk_level}, 置信度: {confidence}%",
            'analysis': json.dumps(data.get('factors', []), ensure_ascii=False) if data.get('factors') else '',
            'suggestions': json.dumps(data.get('recommendations', []), ensure_ascii=False) if data.get('recommendations') else ''
        }

        # 可选填写的患者数据
        patient = data.get('patient_data', {})
        if patient.get('age'):
            payload['mean_radius'] = float(patient.get('age', 0))
        if patient.get('bmi'):
            payload['mean_texture'] = float(patient.get('bmi', 0))

        resp = requests.post(
            f"{supabase_url}/rest/v1/patients",
            json=payload,
            headers=get_supabase_headers(),
            timeout=5
        )

        if resp.status_code not in (200, 201):
            logger.error(f"保存报告失败: {resp.status_code} {resp.text}")
            return jsonify({'success': False, 'error': '保存报告失败'}), 500

        saved = resp.json()
        report_id = saved[0]['id'] if isinstance(saved, list) and saved else None
        logger.info(f"报告已保存, user_id={user_id}, report_id={report_id}")

        return jsonify({'success': True, 'report_id': report_id})

    except Exception as e:
        logger.error(f"保存报告异常: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500

# ============================================================
# 管理员 - 统计 & 用户管理 API
# ============================================================

@app.route('/api/admin/stats', methods=['GET'])
@token_required
@admin_required
def admin_stats():
    """管理员仪表盘统计数据"""
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        headers = get_supabase_headers()

        # 总用户数
        u_resp = requests.get(f"{supabase_url}/rest/v1/users?select=id", headers=headers, timeout=5)
        total_users = len(u_resp.json()) if u_resp.status_code == 200 else 0

        # 总报告数
        p_resp = requests.get(f"{supabase_url}/rest/v1/patients?select=id,risk_level,created_at", headers=headers, timeout=5)
        patients = p_resp.json() if p_resp.status_code == 200 else []
        total_reports = len(patients)

        # 高风险数
        high_risk_count = sum(1 for p in patients if (p.get('risk_level') or '').lower() in ('high', '高风险'))

        # 今日新增
        from datetime import date
        today_str = date.today().isoformat()
        today_reports = sum(1 for p in patients if (p.get('created_at') or '')[:10] == today_str)

        return jsonify({
            'total_users': total_users,
            'total_reports': total_reports,
            'high_risk_count': high_risk_count,
            'today_reports': today_reports
        })
    except Exception as e:
        logger.error(f'管理员统计异常: {str(e)}', exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@app.route('/api/admin/users', methods=['GET'])
@token_required
@admin_required
def admin_list_users():
    """管理员获取所有用户列表"""
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        url = f"{supabase_url}/rest/v1/users?select=id,username,email,phone,age,gender,role,status,plan,plan_expire_at,created_at&order=id"
        resp = requests.get(url, headers=get_supabase_headers(), timeout=5)
        if resp.status_code != 200:
            return jsonify([])
        return jsonify(resp.json())
    except Exception as e:
        logger.error(f'管理员获取用户列表异常: {str(e)}', exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@app.route('/api/admin/users', methods=['POST'])
@token_required
@admin_required
def admin_create_user():
    """管理员新增用户"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        if not username or not email or not password:
            return jsonify({'success': False, 'error': '用户名、邮箱和密码为必填项'}), 400

        supabase_url = os.getenv('SUPABASE_URL')
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        payload = {
            'username': username,
            'email': email,
            'password': hashed,
            'role': data.get('role', 'user'),
            'status': data.get('status', 'active'),
            'phone': data.get('phone', ''),
            'age': data.get('age'),
            'gender': data.get('gender'),
            'plan': data.get('plan', 'free')
        }
        resp = requests.post(f"{supabase_url}/rest/v1/users", json=payload, headers=get_supabase_headers(), timeout=5)
        if resp.status_code not in (200, 201):
            logger.error(f'管理员新增用户失败: {resp.status_code} {resp.text}')
            return jsonify({'success': False, 'error': '新增用户失败，用户名或邮箱可能已存在'}), 500
        return jsonify({'success': True, 'user': resp.json()[0] if isinstance(resp.json(), list) else resp.json()})
    except Exception as e:
        logger.error(f'管理员新增用户异常: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@token_required
@admin_required
def admin_update_user(user_id):
    """管理员编辑用户信息"""
    try:
        data = request.json
        supabase_url = os.getenv('SUPABASE_URL')

        allowed = ['username', 'email', 'phone', 'age', 'gender', 'role', 'status', 'plan']
        payload = {k: v for k, v in data.items() if k in allowed and v is not None}

        # 如果传了新密码则哈希
        if data.get('password'):
            payload['password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        if not payload:
            return jsonify({'success': False, 'error': '没有可更新的字段'}), 400

        url = f"{supabase_url}/rest/v1/users?id=eq.{user_id}"
        resp = requests.patch(url, json=payload, headers=get_supabase_headers(), timeout=5)
        if resp.status_code not in (200, 204):
            return jsonify({'success': False, 'error': '更新失败'}), 500
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f'管理员编辑用户异常: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500

@app.route('/api/admin/users/<int:user_id>/status', methods=['PUT'])
@token_required
@admin_required
def admin_toggle_user_status(user_id):
    """管理员切换用户状态（启用/禁用）"""
    try:
        data = request.json
        new_status = data.get('status')
        if new_status not in ('active', 'inactive', 'banned'):
            return jsonify({'success': False, 'error': '无效的状态值'}), 400

        supabase_url = os.getenv('SUPABASE_URL')
        url = f"{supabase_url}/rest/v1/users?id=eq.{user_id}"
        resp = requests.patch(url, json={'status': new_status}, headers=get_supabase_headers(), timeout=5)
        if resp.status_code not in (200, 204):
            return jsonify({'success': False, 'error': '状态更新失败'}), 500
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f'管理员切换状态异常: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@token_required
@admin_required
def admin_delete_user(user_id):
    """管理员删除用户"""
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        url = f"{supabase_url}/rest/v1/users?id=eq.{user_id}"
        resp = requests.delete(url, headers=get_supabase_headers(), timeout=5)
        if resp.status_code not in (200, 204):
            return jsonify({'success': False, 'error': '删除失败'}), 500
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f'管理员删除用户异常: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500


if __name__ == '__main__':
    port = int(os.getenv("PORT", API_PORT))
    app.run(debug=API_DEBUG, host=API_HOST, port=port)
