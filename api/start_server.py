import sys
import os
import traceback

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())
print("Python路径:", sys.path)

try:
    print("导入Flask...")
    from flask import Flask
    print("Flask导入成功")
    
    print("导入数据库模块...")
    import database
    print("数据库模块导入成功")
    
    print("导入模型模块...")
    from models.simulated_model import predict_probability, get_risk_level
    print("模型模块导入成功")
    
    print("导入app模块...")
    import app
    print("app模块导入成功")
    
    print("启动服务器...")
    app.app.run(host='0.0.0.0', port=5000, debug=True)
except Exception as e:
    print(f"启动失败: {type(e).__name__}: {e}")
    traceback.print_exc()
