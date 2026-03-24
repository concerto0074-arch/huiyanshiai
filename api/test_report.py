import pandas as pd
import numpy as np
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入模拟模型
from models.simulated_model import predict_probability, get_risk_level

def test_report_generation():
    # 测试数据（使用UCI乳腺癌数据集的一条样本）
    test_features = {
        'mean radius': 17.99,
        'mean texture': 10.38,
        'mean perimeter': 122.8,
        'mean area': 1001.0,
        'mean smoothness': 0.1184,
        'mean compactness': 0.2776,
        'mean concavity': 0.3001,
        'mean concave points': 0.1471,
        'mean symmetry': 0.2419,
        'mean fractal dimension': 0.07871
    }
    
    # 创建一个简单的DataFrame
    df = pd.DataFrame([test_features])
    REQUIRED_COLUMNS = list(test_features.keys())
    
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
    def generate_report(prob, risk_level, patient_features):
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
    features = df[REQUIRED_COLUMNS].values
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
    
    # 打印结果
    print("=== 测试报告生成 ===")
    result = results[0]
    print(f"ID: {result['id']}")
    print(f"概率: {result['probability']:.2f}%")
    print(f"风险等级: {result['risk_level']}")
    print(f"\n完整报告:\n{result['report']['full_report']}")
    print("\n=== 测试完成 ===")
    
    # 验证报告结构是否正确
    assert "【预测结果】" in result['report']['full_report'], "报告缺少预测结果部分"
    assert "【关键异常指标分析】" in result['report']['full_report'], "报告缺少关键异常指标分析部分"
    assert "【医学建议】" in result['report']['full_report'], "报告缺少医学建议部分"
    assert "【免责声明】" in result['report']['full_report'], "报告缺少免责声明部分"
    assert "⚠️ 免责声明：" in result['report']['full_report'], "报告缺少完整的免责声明"
    
    print("✅ 报告结构验证通过！")

if __name__ == "__main__":
    test_report_generation()
