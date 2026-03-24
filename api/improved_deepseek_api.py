import requests
import json

def call_deepseek_api(text_to_rewrite):
    """
    调用DeepSeek API进行文本润色
    
    参数:
    text_to_rewrite: str - 需要润色的文本内容
    
    返回:
    str - 润色后的文本内容，如果API调用失败则返回原始文本
    """
    # 修正API URL，移除多余的反引号
    API_URL = "https://api.deepseek.com/v1/chat/completions"
    API_KEY = "sk-cea68c36b6e74d928f3289fe4fe0180a"  # 替换为你的API KEY
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # 构建请求体
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个文本润色助手。请将以下内容用正式风格润色，保持原意不变，并控制在500字以内。"},
            {"role": "user", "content": text_to_rewrite}
        ],
        "max_tokens": 500,
        "temperature": 0.7,
        "stream": False
    }
    
    try:
        print(f"开始调用DeepSeek API进行文本润色...")
        print(f"请求URL: {API_URL}")
        print(f"请求头: {headers}")
        print(f"请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        # 发送API请求
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        print(f"\nAPI响应状态码: {response.status_code}")
        print(f"API响应头: {response.headers}")
        print(f"API响应内容: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                rewritten_text = result['choices'][0]['message']['content']
                print(f"\n✅ 文本润色成功!")
                return rewritten_text.strip()
            except json.JSONDecodeError as e:
                print(f"\n❌ JSON解析失败: {e}")
                return text_to_rewrite
        else:
            print(f"\n❌ API调用失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return text_to_rewrite
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ 网络连接错误: {e}")
        return text_to_rewrite
    except requests.exceptions.Timeout as e:
        print(f"\n❌ 请求超时: {e}")
        return text_to_rewrite
    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")
        return text_to_rewrite

# 测试函数
if __name__ == "__main__":
    # 测试文本
    test_text = "我们的检查结果显示，患者的肿瘤大小比较大，可能是恶性的。建议她尽快去看医生，做进一步的检查，比如穿刺活检。"
    
    print(f"\n=== 原始文本 ===")
    print(test_text)
    
    # 调用API进行润色
    polished_text = call_deepseek_api(test_text)
    
    print(f"\n=== 润色后文本 ===")
    print(polished_text)
