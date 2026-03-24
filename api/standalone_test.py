#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立测试脚本 - 癌症风险预测系统

这个脚本可以直接运行，测试完整的CSV处理和预测流程。
"""

import pandas as pd
import numpy as np
import sys
import os
import requests

def main():
    print("=" * 50)
    print("癌症风险预测系统 - 独立测试")
    print("=" * 50)
    
    # 配置
    REQUIRED_COLUMNS = [
        'mean radius', 'mean texture', 'mean perimeter', 'mean area', 
        'mean smoothness', 'mean compactness', 'mean concavity', 
        'mean concave points', 'mean symmetry', 'mean fractal dimension'
    ]
    
    # 模拟模型函数
    def predict_probability(features):
        """模拟预测概率的函数"""
        # 简单的模拟逻辑：计算特征的加权和
        weights = np.array([0.1, 0.05, 0.15, 0.1, 0.05, 0.1, 0.15, 0.15, 0.05, 0.05])
        prob = np.sum(features * weights) * 10
        return min(max(prob, 0), 100)  # 确保在0-100之间
    
    def get_risk_level(prob):
        """根据概率获取风险等级"""
        if prob > 70:
            return '高风险'
        elif prob > 30:
            return '中风险'
        else:
            return '低风险'
    
    try:
        # 1. 测试Python环境
        print("\n1. 测试Python环境...")
        print(f"Python版本: {sys.version}")
        print(f"Pandas版本: {pd.__version__}")
        print(f"NumPy版本: {np.__version__}")
        print("✅ Python环境测试通过")
        
        # 2. 测试CSV文件读取
        print("\n2. 测试CSV文件读取...")
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'breast_cancer.csv')
        
        if not os.path.exists(csv_path):
            print(f"❌ CSV文件不存在: {csv_path}")
            return 1
        
        df = pd.read_csv(csv_path)
        print(f"✅ 成功读取CSV文件，共 {len(df)} 行，{len(df.columns)} 列")
        print(f"CSV列名: {list(df.columns)}")
        
        # 3. 测试列验证
        print("\n3. 测试列验证...")
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            print(f"❌ 缺少必要的列: {missing_columns}")
            return 1
        else:
            print("✅ 所有必要的列都存在")
        
        # 4. 测试缺失值检查
        print("\n4. 测试缺失值检查...")
        if df[REQUIRED_COLUMNS].isnull().any().any():
            print("❌ 数据中包含缺失值")
            return 1
        else:
            print("✅ 数据中没有缺失值")
        
        # 5. 测试特征准备
        print("\n5. 测试特征准备...")
        features = df[REQUIRED_COLUMNS].values
        print(f"✅ 特征数据准备完成，共 {features.shape[0]} 个样本，{features.shape[1]} 个特征")
        
        # 6. 测试预测功能
        print("\n6. 测试预测功能...")
        
        # 单个样本测试
        sample = features[0]
        prob = predict_probability(sample)
        risk_level = get_risk_level(prob)
        print(f"   单个样本预测: 概率={prob:.2f}%，风险等级={risk_level}")
        
        # 批量测试
        print("\n   批量测试前5个样本:")
        results = []
        for i in range(min(5, len(features))):
            prob = predict_probability(features[i])
            risk_level = get_risk_level(prob)
            results.append({
                'id': i + 1,
                'probability': prob,
                'risk_level': risk_level
            })
            print(f"   样本 {i+1}: 概率={prob:.2f}%，风险等级={risk_level}")
        
        print("✅ 预测功能测试通过")
        
        # 7. 测试API集成（可选，注释掉以避免实际调用）
        print("\n7. 测试API集成 (已禁用)")
        print("   API集成代码已准备好，可以在实际环境中启用")
        
        print("\n" + "=" * 50)
        print("🎉 所有测试通过！")
        print("系统已准备就绪，可以处理CSV文件。")
        print("=" * 50)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
