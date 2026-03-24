import requests
import time

# 等待服务器启动
time.sleep(2)

try:
    # 测试根路径
    response = requests.get('http://localhost:5000/')
    if response.status_code == 200:
        print("✅ 服务器根路径响应正常")
        print(f"响应内容: {response.json()}")
    else:
        print(f"❌ 服务器根路径响应异常，状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
except requests.exceptions.ConnectionError:
    print("❌ 无法连接到服务器，请检查服务器是否正在运行")
except Exception as e:
    print(f"❌ 测试过程中发生错误: {e}")