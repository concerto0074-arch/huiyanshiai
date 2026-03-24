# 简单测试脚本来检查应用是否能正常启动
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

# 尝试导入依赖项
try:
    import requests
    print("✓ requests库已安装")
except ImportError:
    print("✗ requests库未安装")

try:
    from flask import Flask
    print("✓ flask库已安装")
except ImportError:
    print("✗ flask库未安装")

# 尝试导入应用
try:
    from app import app
    print("✓ 应用导入成功")
    print("应用名称:", app.name)
    print("路由列表:", [rule for rule in app.url_map.iter_rules()])
except Exception as e:
    print("✗ 应用导入失败:", str(e))
    import traceback
    traceback.print_exc()
