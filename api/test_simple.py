# 简单测试脚本
print("Hello, World!")
print("Python 环境测试")

# 测试基本导入
try:
    import pandas as pd
    import numpy as np
    print("✅ pandas 和 numpy 导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
