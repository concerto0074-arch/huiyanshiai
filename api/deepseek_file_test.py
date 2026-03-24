import os
import sys
import requests

# 定义输出文件的绝对路径
OUTPUT_FILE = r'c:\Users\12278\Documents\trae_projects\huiyanshiai\api\deepseek_test_results.txt'

def log(message):
    """将日志消息写入文件"""
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{message}\n")

def main():
    # 写入基本信息
    log("=== DeepSeek API测试开始 ===")
    log(f"Python版本: {sys.version}")
    log(f"Requests模块版本: {requests.__version__}")
    log(f"当前工作目录: {os.getcwd()}")
    
    # 测试用户提供的DeepSeek API代码
    try:
        log("\n=== 测试DeepSeek API调用 ===")
        
        API_URL = "https://api.deepseek.com/v1/chat/completions"
        API_KEY = "sk-cea68c36b6e74d928f3289fe4fe0180a"  # 用户提供的API KEY
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        test_text = "这是一个测试文本，用于测试DeepSeek API的文本润色功能。"
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个文本润色助手。请将以下内容用正式风格润色，保持原意不变，并控制在500字以内。"},
                {"role": "user", "content": test_text}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        log(f"API URL: {API_URL}")
        log(f"请求头: {headers}")
        log(f"请求体: {payload}")
        
        # 发送请求
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
        log(f"发生异常: {type(e).__name__}: {str(e)}")
        import traceback
        log(f"异常堆栈: {traceback.format_exc()}")
    
    log("\n=== DeepSeek API测试结束 ===")

if __name__ == "__main__":
    main()
