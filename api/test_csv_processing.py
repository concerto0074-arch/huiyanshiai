# 测试CSV文件处理逻辑
import pandas as pd
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入模型
from models.simulated_model import predict_probability, get_risk_level

# 允许的特征列
REQUIRED_COLUMNS = [
    'mean radius', 'mean texture', 'mean perimeter', 'mean area', 
    'mean smoothness', 'mean compactness', 'mean concavity', 
    'mean concave points', 'mean symmetry', 'mean fractal dimension'
]

def test_csv_processing():
    try:
        # 读取CSV文件
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'breast_cancer.csv')
        df = pd.read_csv(csv_path)
        
        print(f"成功读取CSV文件，共 {len(df)} 行，{len(df.columns)} 列")
        print(f"CSV列名: {list(df.columns)}")
        
        # 检查必要的列
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            print(f"❌ 缺少必要的列: {missing_columns}")
            return False
        else:
            print("✅ 所有必要的列都存在")
        
        # 检查是否有缺失值
        if df[REQUIRED_COLUMNS].isnull().any().any():
            print("❌ 数据中包含缺失值")
            return False
        else:
            print("✅ 数据中没有缺失值")
        
        # 准备特征数据
        features = df[REQUIRED_COLUMNS].values
        print(f"✅ 特征数据准备完成，共 {features.shape[0]} 个样本，{features.shape[1]} 个特征")
        
        # 测试单个样本的预测
        sample = features[0]
        prob = predict_probability(sample)
        risk_level = get_risk_level(prob)
        print(f"✅ 单个样本预测成功：概率={prob:.2f}%，风险等级={risk_level}")
        
        # 测试批量预测
        results = []
        for i, row in enumerate(features[:5]):  # 只测试前5个样本
            prob = predict_probability(row)
            risk_level = get_risk_level(prob)
            patient_features = df.iloc[i][REQUIRED_COLUMNS].tolist()
            results.append({
                'id': i + 1,
                'probability': float(prob),
                'risk_level': risk_level,
                'features_count': len(patient_features)
            })
        
        print("✅ 批量预测测试成功")
        for result in results:
            print(f"   样本 {result['id']}: 概率={result['probability']:.2f}%，风险等级={result['risk_level']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试CSV文件处理逻辑...")
    success = test_csv_processing()
    print(f"测试结果: {'成功' if success else '失败'}")
