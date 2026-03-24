# 慧眼识癌AI辅助系统

## 项目简介

慧眼识癌AI辅助系统是一个基于机器学习的乳腺肿瘤良恶性辅助诊断系统，**无需数据库支持**，使用模拟数据进行预测。

## 功能特点

- **肿瘤风险预测**：通过上传CSV格式的乳腺肿瘤特征数据，系统会自动计算患癌概率和风险等级
- **详细报告生成**：提供完整的预测报告，包括风险评估、异常指标分析和医学建议
- **文本润色功能**：可选择对报告进行专业医学文本润色
- **前端界面**：提供直观的用户界面，方便上传数据和查看结果
- **无需数据库**：系统使用模拟数据和内存处理，无需配置任何数据库

## 技术栈

- **后端**：Flask
- **机器学习**：模拟逻辑回归模型
- **API调用**：Requests（调用DeepSeek API）
- **数据处理**：Pandas, NumPy
- **跨域支持**：Flask-CORS
- **前端**：Vue.js

## 安装和配置

### 1. 安装依赖

确保已安装Python 3.7或更高版本，然后安装所需依赖：

```bash
pip install -r requirements.txt
```

### 2. 配置DeepSeek API（可选）

如果需要使用文本润色功能，在`api/app.py`文件中检查API密钥配置：

```python
API_KEY = "sk-cea68c36b6e74d928f3289fe4fe0180a"  # DeepSeek API密钥
```

**注意**：如果不需要文本润色功能，可以跳过此步骤。

## 使用方法

### 1. 启动服务器

```bash
cd api
python app.py
```

服务器将在`http://localhost:5000`启动。

### 2. 访问前端界面

在浏览器中访问：http://localhost:5000

### 3. 上传数据文件

使用界面上的上传功能，选择包含乳腺肿瘤特征的CSV文件（示例文件：`sample.csv`）。

### 4. 查看预测结果

系统会自动处理数据并显示预测结果，包括患癌概率、风险等级和详细报告。

## API接口

### 预测接口

```
POST /api/predict
```

**请求参数**：
- `file`：CSV格式的肿瘤特征文件
- `polish`（可选）：是否润色报告文本，默认为false

**响应格式**：
```json
{
  "success": true,
  "results": [
    {
      "id": 1,
      "probability": 0.85,
      "risk_level": "高风险",
      "report": {
        "summary": "患癌概率为 85.00%，属于高风险。",
        "analysis": "- mean radius: 20.5 (≥ 15.0 mm) → 肿瘤体积偏大，恶性可能性升高",
        "recommendations": ["建议尽快前往乳腺外科或肿瘤科就诊。"],
        "next_steps": "建议尽快前往乳腺外科或肿瘤科就诊。",
        "full_report": "完整的医学报告"
      }
    }
  ],
  "message": "预测完成"
}
```

### 文本润色接口

```
POST /api/polish
```

**请求参数**：
```json
{
  "text": "需要润色的文本"
}
```

**响应格式**：
```json
{
  "success": true,
  "original_text": "原始文本",
  "polished_text": "润色后的文本",
  "message": "文本润色完成"
}
```

## CSV数据格式

上传的CSV文件需要包含以下特征列：

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

示例数据已提供在`sample.csv`文件中。

## 项目结构

```
huiyanshiai/
├── api/
│   ├── app.py            # Flask应用主文件
│   └── simple_start.py   # 启动脚本
├── frontend/             # 前端界面目录
├── models/
│   └── simulated_model.py # 模拟预测模型
├── sample.csv            # 示例数据文件
├── requirements.txt      # 依赖列表
└── README.md             # 项目说明
```

## 模拟模型说明

系统使用`models/simulated_model.py`中的模拟模型进行预测：

- **预测算法**：模拟逻辑回归模型
- **输入特征**：10个乳腺肿瘤特征
- **输出结果**：患癌概率（0-1之间的数值）和风险等级（低风险/中风险/高风险）

## 注意事项

1. 本系统使用模拟数据进行预测，仅供教学和演示使用，不能替代专业医生的临床诊断
2. 系统无需数据库支持，所有数据仅在内存中处理
3. 文本润色功能需要网络连接和有效的DeepSeek API密钥
4. 请确保上传的CSV文件格式正确，包含所有必要的特征列

## 停止服务器

在运行服务器的终端中，按 Ctrl+C 停止服务器。

## 开发说明

### 核心功能修改

- 移除了所有数据库相关代码（SQLAlchemy、数据库模型、数据库初始化等）
- 简化了API接口，不再需要用户认证
- 所有数据处理和预测仅在内存中进行
- 保留了文本润色功能，可选择使用

### 模型自定义

如果需要替换预测模型，可以修改`models/simulated_model.py`文件中的`predict_probability`和`get_risk_level`函数。

## 许可证

本项目仅供学习和研究使用。