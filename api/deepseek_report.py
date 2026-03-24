from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pandas as pd
import numpy as np
import sys
import os
import json
import hashlib
from datetime import timedelta
from openai import OpenAI

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入模拟模型
from models.simulated_model import predict_probability, get_risk_level

# 创建应用实例
app = Flask(__name__)
CORS(app, supports_credentials=True)  # 启用CORS并支持凭证
app.secret_key = 'your_secret_key_here'  # 设置会话密钥
app.permanent_session_lifetime = timedelta(days=7)  # 设置会话有效期

# 初始化DeepSeek客户端
# 注意：需要设置DEEPSEEK_API_KEY环境变量
deepseek_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", "your-api-key-here"),
    base_url="https://api.deepseek.com/v1"
)

# 允许的特征列
REQUIRED_COLUMNS = [
    'mean radius', 'mean texture', 'mean perimeter', 'mean area', 
    'mean smoothness', 'mean compactness', 'mean concavity', 
    'mean concave points', 'mean symmetry', 'mean fractal dimension'
]

# 使用DeepSeek润色报告的函数
def polish_report_with_deepseek(report):
    """
    使用DeepSeek API润色医学报告
    """
    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一名专业的医学报告润色专家，请将提供的乳腺肿瘤风险评估报告润色得更专业、更清晰，同时保持原意不变。润色时要注意医学术语的准确性和规范性，确保报告结构清晰，易于理解。"
                },
                {
                    "role": "user",
                    "content": report
                }
            ],
            temperature=0.3,  # 降低随机性，保持专业性
            max_tokens=1000
        )
        
        polished_report = response.choices[0].message.content
        return polished_report
    except Exception as e:
        print(f"DeepSeek润色失败: {e}")
        return report  # 如果润色失败，返回原始报告

# 生成报告的函数
def generate_report(prob, risk_level, patient_features):
    # 构建患者特征字典
    patient_data = {col: patient_features[i] for i, col in enumerate(REQUIRED_COLUMNS)}
    
    # 临床参考阈值
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
    
    # 使用DeepSeek润色报告
    polished_full_report = polish_report_with_deepseek(full_report)
    
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
        'full_report': full_report,
        'polished_full_report': polished_full_report  # 添加润色后的报告
    }

@app.route('/predict_with_deepseek', methods=['POST'])
def predict_with_deepseek():
    """
    预测API，使用DeepSeek润色报告
    """
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
        
        # 进行预测
        results = []
        for i, row in enumerate(features):
            prob = predict_probability(row)
            risk_level = get_risk_level(prob)
            # 传递完整的特征数据给报告生成函数
            patient_features = df.iloc[i][REQUIRED_COLUMNS].tolist()
            report = generate_report(prob, risk_level, patient_features)
            results.append({
                'id': i + 1,
                'probability': float(prob),
                'risk_level': risk_level,
                'report': report
            })
        
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return "DeepSeek Report Generation API is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
