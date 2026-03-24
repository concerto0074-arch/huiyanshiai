import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 从app.py中导入DeepSeek文本润色函数
from app import polish_text_with_deepseek

def test_polish_text_with_deepseek():
    """
    测试从app.py导入的DeepSeek文本润色功能
    """
    # 测试文本1: 简单的医学描述
    test_text1 = "我们的检查结果显示，患者的肿瘤大小比较大，可能是恶性的。建议她尽快去看医生，做进一步的检查，比如穿刺活检。"
    
    # 测试文本2: 更详细的医学报告
    test_text2 = "【预测结果】
患癌概率为 85.00%，属于高风险。

【关键异常指标分析】
- mean radius: 17.99 (≥ 15.0 mm) → 肿瘤体积偏大，恶性可能性升高
- mean perimeter: 122.8 (≥ 100 mm) → 周长增加通常伴随半径和面积增大
- mean area: 1001.0 (≥ 800 mm²) → 肿瘤面积显著增大，需警惕

【医学建议】
建议尽快前往乳腺外科或肿瘤科就诊，安排进一步检查（如穿刺活检、MRI），以明确病理诊断。

【免责声明】
⚠️ 免责声明：本报告由'慧眼识癌'AI辅助系统自动生成，基于统计模型与公开医学知识库，仅供参考。不能替代专业医生的临床诊断、影像判读或病理检查。最终诊疗决策请以执业医师意见为准。"
    
    print("=== 测试DeepSeek文本润色功能 ===")
    
    # 测试1: 简单医学描述
    print("\n1. 测试简单医学描述:")
    print("原始文本:")
    print(test_text1)
    
    polished1 = polish_text_with_deepseek(test_text1)
    
    print("\n润色后文本:")
    print(polished1)
    print("\n" + "-" * 50)
    
    # 测试2: 详细医学报告
    print("\n2. 测试详细医学报告:")
    print("原始文本:")
    print(test_text2)
    
    polished2 = polish_text_with_deepseek(test_text2)
    
    print("\n润色后文本:")
    print(polished2)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_polish_text_with_deepseek()