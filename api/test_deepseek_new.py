# 测试DeepSeek API调用
from openai import OpenAI

def test_deepseek_api():
    try:
        client = OpenAI(
            api_key="sk-9ec0601586d04b7eac0e5a8973bed379",
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, please introduce yourself briefly."},
            ],
            stream=False
        )
        
        print("✅ DeepSeek API调用成功！")
        print(f"响应内容: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ DeepSeek API调用失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_deepseek_api()