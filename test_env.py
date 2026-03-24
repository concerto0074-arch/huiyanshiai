import sys
import os

# 打印基本信息
print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")
print(f"当前文件路径: {os.path.abspath(__file__)}")

# 尝试导入基本库
try:
    import flask
    print(f"Flask版本: {flask.__version__}")
except Exception as e:
    print(f"Flask导入失败: {e}")

try:
    import pandas
    print(f"Pandas版本: {pandas.__version__}")
except Exception as e:
    print(f"Pandas导入失败: {e}")

try:
    import numpy
    print(f"NumPy版本: {numpy.__version__}")
except Exception as e:
    print(f"NumPy导入失败: {e}")

try:
    import requests
    print(f"Requests版本: {requests.__version__}")
except Exception as e:
    print(f"Requests导入失败: {e}")

try:
    from flask_cors import CORS
    print(f"Flask-CORS导入成功")
except Exception as e:
    print(f"Flask-CORS导入失败: {e}")

print("\n测试完成")