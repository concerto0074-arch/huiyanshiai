import sys
import os

# 打印基本信息
print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")
print(f"当前文件路径: {os.path.abspath(__file__)}")

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(f"更新后的Python路径: {sys.path}")

# 尝试导入必要的模块
try:
    print("\n尝试导入Flask...")
    from flask import Flask
    print("Flask导入成功")
    
    print("\n尝试导入数据库模块...")
    import database
    print("数据库模块导入成功")
    
    print("\n尝试导入模型模块...")
    from models.simulated_model import predict_probability, get_risk_level
    print("模型模块导入成功")
    
    print("\n尝试导入app模块...")
    import app
    print("app模块导入成功")
    
    print("\n尝试初始化数据库...")
    database.init_db()
    print("数据库初始化成功")
    
    print("\n尝试启动服务器...")
    print("服务器将在 http://localhost:5000 上运行")
    print("按 Ctrl+C 停止服务器")
    app.app.run(host='0.0.0.0', port=5000, debug=True)
except Exception as e:
    print(f"\n启动失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
