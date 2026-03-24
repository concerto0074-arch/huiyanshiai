# 模拟的癌症预测模型
import numpy as np

def predict_probability(features):
    """模拟逻辑斯蒂回归预测"""
    # 简单的加权计算来模拟模型预测
    weights = np.array([0.1, 0.05, 0.08, 0.001, 0.5, 0.8, 1.0, 1.2, 0.3, 0.01])
    bias = -20.0
    
    # 计算加权和
    weighted_sum = np.dot(features, weights) + bias
    
    # 使用sigmoid函数转换为概率
    probability = 1 / (1 + np.exp(-weighted_sum))
    
    return probability

def get_risk_level(probability):
    """根据概率确定风险等级"""
    if probability < 0.3:
        return "低风险"
    elif probability < 0.7:
        return "中风险"
    else:
        return "高风险"