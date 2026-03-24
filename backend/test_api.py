#!/usr/bin/env python3
# 简单的API测试脚本

import requests
import json

# API基础URL
API_BASE_URL = 'http://localhost:5000/api'

# 测试患者数据
test_patient_data = {
    "age": 60,
    "gender": "male",
    "smoke": "current",
    "bmi": 28.5,
    "familyHistory": "yes",
    "alcohol": "heavy",
    "tumorMarker1": 150.5,
    "tumorMarker2": 60.2,
    "tumorMarker3": 85.7,
    "mutation1": "positive",
    "mutation2": "negative"
}

def test_predict_endpoint():
    """测试预测API端点"""
    print("测试预测API端点...")
    
    # 只测试后端支持的算法
    algorithms = ['random_forest', 'svm', 'logistic_regression']
    
    for algorithm in algorithms:
        print(f"\n测试算法: {algorithm}")
        
        # 构建请求数据
        request_data = {
            "algorithm": algorithm,
            "patient_data": test_patient_data
        }
        
        try:
            # 发送请求
            response = requests.post(f"{API_BASE_URL}/predict", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ 预测成功:")
                print(f"  风险等级: {result['risk_level']}")
                print(f"  风险评分: {result['risk_score']}")
                print(f"  置信度: {result['confidence']:.2f}%")
                print(f"  概率分布: 低风险 {result['probabilities']['low']:.2f}%, 中风险 {result['probabilities']['medium']:.2f}%, 高风险 {result['probabilities']['high']:.2f}%")
            else:
                print(f"✗ 预测失败: HTTP {response.status_code}")
                print(f"  错误信息: {response.text}")
        except Exception as e:
            print(f"✗ 预测失败: {str(e)}")

def test_models_endpoint():
    """测试获取模型列表API端点"""
    print("\n\n测试获取模型列表API端点...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/models")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 获取模型列表成功:")
            print(f"  总模型数: {result['total']}")
            print("  可用模型:")
            for model in result['models']:
                print(f"  - {model['name']}: {model['description']}")
        else:
            print(f"✗ 获取模型列表失败: HTTP {response.status_code}")
            print(f"  错误信息: {response.text}")
    except Exception as e:
        print(f"✗ 获取模型列表失败: {str(e)}")

def test_health_endpoint():
    """测试健康检查API端点"""
    print("\n\n测试健康检查API端点...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 健康检查成功:")
            print(f"  状态: {result['status']}")
            print(f"  加载的模型数: {result['models_loaded']}")
            print(f"  可用模型: {result['models']}")
            print(f"  时间戳: {result['timestamp']}")
        else:
            print(f"✗ 健康检查失败: HTTP {response.status_code}")
            print(f"  错误信息: {response.text}")
    except Exception as e:
        print(f"✗ 健康检查失败: {str(e)}")

if __name__ == "__main__":
    print("开始测试后端API...")
    print("=" * 50)
    
    # 测试各端点
    test_health_endpoint()
    test_models_endpoint()
    test_predict_endpoint()
    
    print("\n" + "=" * 50)
    print("API测试完成!")
