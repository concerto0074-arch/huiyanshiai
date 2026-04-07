# 问题排查指南

## 问题描述
请求失败，没有响应，可能与CSV文件处理有关。

## 排查步骤

### 1. 检查Python环境和依赖

#### 安装依赖
```bash
# 确保使用正确的Python环境
pip install -r requirements.txt
```

#### 验证安装
```bash
python -c "
import pandas as pd
import numpy as np
import flask
import requests
print('Pandas版本:', pd.__version__)
print('NumPy版本:', np.__version__)
print('Flask版本:', flask.__version__)
print('Requests版本:', requests.__version__)
"
```

### 2. 测试CSV文件格式

使用提供的样本CSV文件 `data/breast_cancer.csv`，确保：
- 包含所有必要的列
- 没有缺失值
- 格式正确

### 3. 测试CSV文件读取功能

运行 `api/standalone_test.py` 脚本：

```bash
cd api
python standalone_test.py
```

这个脚本会：
- 测试Python环境
- 测试CSV文件读取
- 测试列验证
- 测试缺失值检查
- 测试特征准备
- 测试预测功能

### 4. 测试服务器启动

使用统一入口启动本地服务：

```bash
./start_local.ps1
```

正常启动后请优先检查：
```
首页: http://127.0.0.1:5000/
算法页: http://127.0.0.1:5000/algorithms.html
状态: http://127.0.0.1:5000/api/system-status
```

### 5. 测试API请求

使用 curl 测试状态接口：

```bash
curl http://127.0.0.1:5000/api/system-status
```

如果状态接口正常，再测试业务接口。

### 6. 检查错误日志

服务器启动后，查看控制台输出的错误信息。如果没有输出，可以检查服务器日志文件。

## 常见问题和解决方案

### 问题1：依赖安装失败
**解决方案：** 确保使用正确的Python环境，尝试使用虚拟环境：

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 问题2：CSV文件格式错误
**解决方案：** 确保CSV文件包含所有必要的列：
- mean radius
- mean texture
- mean perimeter
- mean area
- mean smoothness
- mean compactness
- mean concavity
- mean concave points
- mean symmetry
- mean fractal dimension

### 问题3：服务器无法启动
**解决方案：** 检查端口是否被占用，尝试使用不同的端口：

```bash
./start_local.ps1
```

如需改端口，请修改根目录 `.env` 中的 `PORT`，当前统一默认值为 `5000`。

### 问题4：API请求失败
**解决方案：** 
1. 检查服务器是否正在运行
2. 先检查状态接口是否正常（http://127.0.0.1:5000/api/system-status）
3. 检查请求方法是否为POST
4. 检查文件字段名称是否为"file"

## 简化版测试脚本

使用以下脚本测试CSV处理逻辑：

```python
import pandas as pd
import numpy as np
import os

# 必要的列
REQUIRED_COLUMNS = [
    'mean radius', 'mean texture', 'mean perimeter', 'mean area', 
    'mean smoothness', 'mean compactness', 'mean concavity', 
    'mean concave points', 'mean symmetry', 'mean fractal dimension'
]

# 模拟模型函数
def predict_probability(features):
    weights = np.array([0.1, 0.05, 0.15, 0.1, 0.05, 0.1, 0.15, 0.15, 0.05, 0.05])
    prob = np.sum(features * weights) * 10
    return min(max(prob, 0), 100)

def get_risk_level(prob):
    if prob > 70:
        return '高风险'
    elif prob > 30:
        return '中风险'
    else:
        return '低风险'

# 读取CSV文件
def test_csv_processing(csv_path):
    try:
        df = pd.read_csv(csv_path)
        print(f"成功读取CSV文件，共 {len(df)} 行，{len(df.columns)} 列")
        
        # 检查必要的列
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            print(f"缺少必要的列: {missing_columns}")
            return False
        
        # 检查缺失值
        if df[REQUIRED_COLUMNS].isnull().any().any():
            print("数据中包含缺失值")
            return False
        
        # 测试预测
        features = df[REQUIRED_COLUMNS].values
        for i in range(min(3, len(features))):
            prob = predict_probability(features[i])
            risk_level = get_risk_level(prob)
            print(f"样本 {i+1}: 概率={prob:.2f}%，风险等级={risk_level}")
        
        return True
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

# 运行测试
if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'breast_cancer.csv')
    print(f"测试文件: {csv_path}")
    success = test_csv_processing(csv_path)
    print(f"测试结果: {'成功' if success else '失败'}")
```

## 使用Postman测试

1. 下载并安装Postman：https://www.postman.com/downloads/
2. 打开Postman，创建一个新的请求
3. 先设置请求方法为GET
4. 输入URL: http://127.0.0.1:5000/api/system-status
5. 点击"Body"选项卡
6. 确认状态正常后，再切换到具体业务接口测试

## 服务器日志

服务器启动后，控制台会输出日志信息。如果遇到错误，会显示详细的错误信息，包括：
- 错误类型
- 错误位置
- 错误描述

请保存这些信息以便进一步排查问题。

## 联系支持

如果以上步骤都无法解决问题，请提供以下信息：
1. Python版本
2. 依赖版本
3. 完整的错误日志
4. 请求的详细信息（包括请求头、请求体）
5. CSV文件的前几行数据