import requests
import json

def test_predict_api():
    # 定义API端点URL
    url = "http://127.0.0.1:5000/predict"
    
    # 准备测试数据
    test_data = {
        "data": [
            [17.99, 10.38, 122.8, 1001.0, 0.1184, 0.2776, 0.3001, 0.1471, 0.2419, 0.07871]
        ]
    }
    
    print("=== 测试API预测功能 ===")
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(test_data, indent=2)}")
    
    try:
        # 发送POST请求
        response = requests.post(url, json=test_data)
        
        # 检查响应状态码
        if response.status_code == 200:
            # 解析响应数据
            result = response.json()
            print(f"\n响应状态码: {response.status_code}")
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 验证响应结构
            assert "results" in result, "响应缺少results字段"
            assert len(result["results"]) > 0, "响应results为空"
            
            # 验证报告结构
            result_item = result["results"][0]
            assert "report" in result_item, "结果缺少report字段"
            assert "full_report" in result_item["report"], "报告缺少full_report字段"
            
            # 验证报告内容是否符合模板要求
            full_report = result_item["report"]["full_report"]
            assert "【预测结果】" in full_report, "报告缺少预测结果部分"
            assert "【关键异常指标分析】" in full_report, "报告缺少关键异常指标分析部分"
            assert "【医学建议】" in full_report, "报告缺少医学建议部分"
            assert "【免责声明】" in full_report, "报告缺少免责声明部分"
            assert "⚠️ 免责声明：" in full_report, "报告缺少完整的免责声明"
            
            print("\n✅ API测试通过！报告生成符合要求。")
            return True
        else:
            print(f"\n❌ API请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请确保服务器正在运行。")
        return False
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        return False

def test_api_endpoints():
    # 测试根路径
    url = "http://127.0.0.1:5000/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ 根路径测试通过")
        else:
            print(f"❌ 根路径测试失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 根路径测试发生错误: {str(e)}")

if __name__ == "__main__":
    # 先测试API端点
    test_api_endpoints()
    print()
    # 测试预测功能
    test_predict_api()
