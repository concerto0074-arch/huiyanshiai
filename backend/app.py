from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
import os
from flask_cors import CORS
import logging

from config import (
    MODELS_DIR, MODEL_SUFFIX, RESULTS_FILE, 
    FEATURES, model_descriptions, API_HOST, API_PORT, API_DEBUG
)
from utils import (
    load_model, load_results, ensure_dir, setup_logging,
    map_smoking_status, map_gender, map_mutation
)

# 设置日志
logger = setup_logging()

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 加载所有模型
models = {}
model_info = {}

# 模型性能结果
model_results = {}

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
    
    logger.info(f"共加载{len(models)}个模型")

# 初始化加载模型
load_models()

@app.route('/api/models', methods=['GET'])
def get_models():
    """获取所有可用模型"""
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'models_loaded': len(models),
        'models': list(models.keys()),
        'timestamp': pd.Timestamp.now().isoformat()
    })

if __name__ == '__main__':
    load_models()
    app.run(debug=API_DEBUG, host=API_HOST, port=API_PORT)
