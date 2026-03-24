import requests
import sys

# 测试DeepSeek API调用
def test_deepseek_api():
    try:
        # 使用用户提供的API URL和API Key
        api_url = "https://api.deepseek.com/v1/chat/completions"
        api_key = "sk-cea68c36b6e74d928f3289fe4fe0180a"
        
        # 使用用户提供的提示词和系统角色
        text_to_rewrite = "这是一个测试文本，用于测试DeepSeek API的文本润色功能。"
        
        response = requests.post(
            api_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个文本润色助手。请将以下内容用正式风格润色，保持原意不变，并控制在500字以内。"},
                    {"role": "user", "content": text_to_rewrite}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=30
        )
        
        # 同时打印到标准输出和标准错误流
        print(f"响应状态码: {response.status_code}")
        print(f"响应状态码: {response.status_code}", file=sys.stderr)
        
        print(f"响应头: {response.headers}")
        print(f"响应头: {response.headers}", file=sys.stderr)
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"响应内容: {response_data}")
            print(f"响应内容: {response_data}", file=sys.stderr)
            
            # 提取润色后的文本
            rewritten_text = response_data['choices'][0]['message']['content']
            print(f"润色后的文本: {rewritten_text.strip()}")
            print(f"润色后的文本: {rewritten_text.strip()}", file=sys.stderr)
            
            return True
        else:
            print(f"API调用失败: {response.text}")
            print(f"API调用失败: {response.text}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        print(f"测试过程中发生错误: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        traceback.print_exc(file=sys.stderr)
        return False

if __name__ == "__main__":
    print("开始测试DeepSeek API...")
    print("开始测试DeepSeek API...", file=sys.stderr)
    success = test_deepseek_api()
    print(f"测试结果: {'成功' if success else '失败'}")
    print(f"测试结果: {'成功' if success else '失败'}", file=sys.stderr)
