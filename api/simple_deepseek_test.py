import os
import sys
from openai import OpenAI
import requests

# 定义输出文件
OUTPUT_FILE = "simple_deepseek_test_output.txt"

def log(message):
    """将消息同时打印到控制台和文件"""
    print(message)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{message}\n")

log("=== 开始简单DeepSeek测试 ===")

# 测试环境变量
log(f"当前工作目录: {os.getcwd()}")
log(f"Python版本: {sys.version}")
log(f"DEEPSEEK_API_KEY环境变量是否存在: {'DEEPSEEK_API_KEY' in os.environ}")

# 测试OpenAI导入
log("OpenAI导入成功")

# 尝试初始化DeepSeek客户端
try:
    log("\n=== 测试OpenAI客户端方式 ===")
    log("尝试初始化DeepSeek客户端...")
    deepseek_client = OpenAI(
        api_key="sk-cea68c36b6e74d928f3289fe4fe0180a",
        base_url="https://api.deepseek.com/v1"
    )
    log("DeepSeek客户端初始化成功")
    log(f"客户端类型: {type(deepseek_client)}")
    
    # 打印可用的方法
    log(f"客户端可用属性: {dir(deepseek_client)[:10]}...")
    
except Exception as e:
    log(f"DeepSeek客户端初始化失败: {e}")
    import traceback
    traceback.print_exc()

# 测试用户提供的requests版本API调用
try:
    log("\n=== 测试Requests方式 (用户提供的代码) ===")
    API_URL = "https://api.deepseek.com/v1/chat/completions"
    API_KEY = "sk-cea68c36b6e74d928f3289fe4fe0180a"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个文本润色助手。请将以下内容用正式风格润色，保持原意不变，并控制在500字以内。"},
            {"role": "user", "content": "这是一个测试文本，用于测试DeepSeek API的文本润色功能。"}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    log(f"API URL: {API_URL}")
    log(f"请求头: {headers}")
    log(f"请求体: {payload}")
    
    # 发送请求
    log("发送API请求...")
    response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
    log(f"响应状态码: {response.status_code}")
    log(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        rewritten_text = result['choices'][0]['message']['content']
        log(f"润色后的文本: {rewritten_text.strip()}")
    else:
        log(f"API调用失败，状态码: {response.status_code}")
        log(f"错误信息: {response.text}")
        
except Exception as e:
    log(f"API调用发生异常: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

log("\n=== 简单DeepSeek测试完成 ===")
