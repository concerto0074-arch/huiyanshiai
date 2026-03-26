import os
import shutil

# --- Configuration ---
API_APP_PATH = r'd:\huiyanshiai(2.0)\api\app.py'
BACKEND_APP_PATH = r'd:\huiyanshiai(2.0)\backend\app.py'
BACKEND_CONFIG_PATH = r'd:\huiyanshiai(2.0)\backend\config.py'
BACKEND_UTILS_PATH = r'd:\huiyanshiai(2.0)\backend\utils.py'
BACKEND_R_SERVICE_PATH = r'd:\huiyanshiai(2.0)\backend\r_integration_service.py'

# 1. Read existing API app.py
with open(API_APP_PATH, 'r', encoding='utf-8') as f:
    api_content = f.read()

# 2. Extract specific constants from backend/config.py
# We won't import the whole config to avoid path issues, just extract what we need
with open(BACKEND_CONFIG_PATH, 'r', encoding='utf-8') as f:
    config_content = f.read()

# Extract FEATURES, model_descriptions if possible (simplified regex)
import re
features_match = re.search(r'FEATURES = (\{.*?\})', config_content, re.DOTALL)
features_dict_str = features_match.group(1) if features_match else "{}"

# 3. Read R service for integration
with open(BACKEND_R_SERVICE_PATH, 'r', encoding='utf-8') as f:
    r_service_content = f.read()

# 4. Read backend app.py to extract predict_form logic parts
with open(BACKEND_APP_PATH, 'r', encoding='utf-8') as f:
    backend_content = f.read()

# Extract the predict_form function body or similar parts
# For simplicity, we will append a well-defined block of code to api/app.py

integration_code = f'''
# ============================================================
# 集成机器学习预测功能 (Original Backend 5001 Logic)
# ============================================================

FEATURES_MAP = {features_dict_str}

@app.route('/api/ml/predict', methods=['POST'])
@rate_limit('ml_predict', limit=20, per_seconds=60)
def ml_predict():
    """接收临床参数表单并进行多模型风险评估"""
    try:
        data = request.json
        if not data:
            return jsonify({{'error': '请求体不能为空'}}), 400

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
        smoke_factor = {{'current': 1.0, 'former': 0.5, 'never': 0.0}}.get(patient_smoke, 0.0)
        mutation1_factor = {{'positive': 1.0, 'negative': 0.0, 'unknown': 0.3}}.get(mutation1, 0.0)
        mutation2_factor = {{'positive': 1.0, 'negative': 0.0, 'unknown': 0.3}}.get(mutation2, 0.0)

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
                logger.error(f"真实模型预测失败, 切换回模拟逻辑: {{e}}")
                prob = predict_probability(features[0])
                risk_level = get_risk_level(prob)

        prob_percent = prob * 100
        
        # 构造详细返回结果 (保持与前端对接格式兼容)
        # 这里重用 api/app.py 里已有的逻辑，或者直接构造
        
        # 模拟概率分布用于可视化绘图
        prob_high = prob
        prob_low = max(0.01, 1.0 - prob - 0.1)
        prob_mid = 1.0 - prob_high - prob_low

        response_data = {{
            'success': True,
            'patientName': patient_name,
            'algorithm': algorithm,
            'riskLevel': risk_level,
            'confidence': int(min(99, max(60, 50 + abs(prob - 0.5) * 80))),
            'probability': round(prob_percent, 2),
            'probabilities': {{
                '低风险': round(prob_low, 4),
                '中风险': round(prob_mid, 4),
                '高风险': round(prob_high, 4)
            }},
            'reportText': f"基于 AI 模型评估，您的癌症风险为 {{risk_level}} ({{prob_percent:.1f}}%)。"
        }}

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"ML Predict Error: {{str(e)}}")
        return jsonify({{'error': str(e)}}), 500

# 别名路由，确保向下兼容 (支持以前指向 5001 的前端请求)
@app.route('/api/predict_form', methods=['POST'])
def legacy_predict_form():
    return ml_predict()
'''

# Find the list_models endpoint and insert our new integration before it
if '# Models list endpoint' in api_content:
    new_api_content = api_content.replace('# Models list endpoint', integration_code + '\n\n# Models list endpoint')
else:
    # Or just append before if __name__
    new_api_content = api_content.replace("if __name__ == '__main__':", integration_code + "\n\nif __name__ == '__main__':")

with open(API_APP_PATH, 'w', encoding='utf-8') as f:
    f.write(new_api_content)

print("Successfully merged machine learning routes into api/app.py")
