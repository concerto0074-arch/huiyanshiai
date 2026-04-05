from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
import os
from flask_cors import CORS
import logging
import requests
from dotenv import load_dotenv

# 加载 .env 环境变量
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

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
CORS(app)  # 允许跨域请求

# 初始化全局变量
models = {}
model_info = {}
model_results = {}

# 移除 init_models，改为直接在文件级别加载（或仅在 __main__ 及需要时加载）
# 这里我们直接调用 load_models() 以确保所有 worker 都能加载它，或者交给 WSGI 容器加载
with app.app_context():
    pass # 如果需要的话

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
    return jsonify({
        'status': 'ok',
        'models_loaded': len(models),
        'models': list(models.keys()),
        'timestamp': pd.Timestamp.now().isoformat()
    })

# ============================================================
# 登录功能（后端实现）
# ============================================================

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录接口，使用 Supabase REST API 验证用户名和密码"""
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

        # 使用 Supabase REST API 查询匹配的用户记录
        query_url = f"{supabase_url}/rest/v1/users?username=eq.{username}&password=eq.{password}&select=id,username,email,role"
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
        token = f"dummy-token-{user['id']}"
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user.get('username'),
                'email': user.get('email'),
                'role': user.get('role', 'user')
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
    """用户注册接口，向 Supabase 插入新用户记录"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone', '')
        if not username or not email or not password:
            return jsonify({'success': False, 'error': '缺少必填字段'}), 400

        supabase_url = os.getenv('SUPABASE_URL')
        anon_key = os.getenv('SUPABASE_ANON_KEY')
        if not supabase_url or not anon_key:
            logger.error('Supabase 配置缺失')
            return jsonify({'success': False, 'error': '服务器未配置 Supabase'}), 500

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
            'password': password,
            'phone': phone,
            'role': 'user'
        }
        resp = requests.post(insert_url, json=payload, headers=headers, timeout=5)
        if resp.status_code not in (200, 201):
            logger.error(f'Supabase 注册失败，状态码 {resp.status_code}, 响应: {resp.text}')
            return jsonify({'success': False, 'error': '注册失败，请稍后重试'}), 500

        user = resp.json()[0] if isinstance(resp.json(), list) else resp.json()
        token = f"dummy-token-{user.get('id')}"
        return jsonify({
            'success': True,
            'user': {
                'id': user.get('id'),
                'username': user.get('username'),
                'email': user.get('email'),
                'role': user.get('role', 'user')
            },
            'token': token
        })
    except Exception as e:
        logger.error(f'注册异常: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500


if __name__ == '__main__':
    port = int(os.getenv("PORT", API_PORT))
    app.run(debug=API_DEBUG, host=API_HOST, port=port)
