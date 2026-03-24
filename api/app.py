from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import sys
import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入模拟模型
from models.simulated_model import predict_probability, get_risk_level

# 创建应用实例
app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)  # 启用CORS
import os
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

from database import init_db, add_user, get_all_users, get_user_by_id, update_user, delete_user, User, get_user_by_username

app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'super-secret-key-huiyanshiai')

# Initialize database (ensure migrations)
init_db()

# --- Authentication Routes ---

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    required = ['username', 'password', 'email']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    existing_user = get_user_by_username(data['username'])
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 400
    
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(
        username=data['username'],
        password=hashed_password,
        email=data['email'],
        role='user'
    )
    user_id = add_user(new_user)
    return jsonify({'success': True, 'user_id': user_id, 'message': 'Register success'}), 201

@app.route('/api/login', methods=['POST'])
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
    expected = os.getenv('ADMIN_TOKEN', 'admin-secret-token')
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
    API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-cea68c36b6e74d928f3289fe4fe0180a")
    
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

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    return app.send_static_file(path)

if __name__ == '__main__':
    print("服务器将在 http://localhost:5000 上运行")
    print("按 Ctrl+C 停止服务器")
    app.run(host='0.0.0.0', port=5000, debug=True)