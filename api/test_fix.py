# 测试修复后的代码是否能正常导入
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 尝试导入Flask应用
print("尝试导入Flask应用...")
try:
    from app import app
    print("✅ Flask应用导入成功")
except Exception as e:
    print(f"❌ Flask应用导入失败: {e}")
    sys.exit(1)

# 检查generate_report函数是否只定义了一次
print("\n检查generate_report函数是否只定义了一次...")
try:
    with open('app.py', 'r') as f:
        content = f.read()
    
    # 计算generate_report函数的定义次数
    count = content.count('def generate_report(')
    if count == 1:
        print("✅ generate_report函数只定义了一次")
    else:
        print(f"❌ generate_report函数定义了{count}次")
        sys.exit(1)
except Exception as e:
    print(f"❌ 检查函数定义时出错: {e}")
    sys.exit(1)

print("\n🎉 所有测试通过！代码修复成功")