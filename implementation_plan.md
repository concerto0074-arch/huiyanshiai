# R 算法解析与 Python 集成方案规划

## 1. R 算法梳理与原理解析

您上传的 R 代码主要用于非小细胞肺癌（NSCLC）由于各个亚型（ADC腺癌、SCC鳞癌、COID类癌）和正常肺组织（NL）的基因表达数据分析。其核心算法流程如下：

*   **目标对象**：NSCLC 的基因表达图谱（如 `1157gene.csv` 和 `cleandata.csv`），每行代表一个样本，每列代表一个基因。
*   **WGCNA (加权基因共表达网络分析)**：在 `不重叠分群` 等文件夹中，通过 `blockwiseModules` 等函数将几千个基因划分为不同的「基因共表达模块」。
*   **MSGL (多项式稀疏群 Lasso)**：这是核心的分类与特征选择算法（见 `MSGL.R`, `AMRSOGL.R`, `proposed.R`）。代码通过引入由于 WGCNA 构建的模块信息（或互信息权重 `quanzhong.csv`），使用十折交叉验证 (`msgl::cv`) 训练多分类模型。
*   **输出结果**：程序最终评估模型在预测四大类（ADC, NL, SCC, COID）时的准确率、召回率、混淆矩阵，并输出重要特征基因（`nr.csv`）和特定模型的 AUC 值。

## 2. Python 后端现有架构与「空盒子」

目前的 Python 后端 (`backend/app.py` 和 `train.py`) 主要是为一个**临床表格数据**（如年龄、BMI、吸烟史等）构建的简化模型（Random Forest, SVM, Logistic Regression），输出低/中/高三种风险评估。
这些算法与您学术论文中深度挖掘「基因表达数据」的 R 算法是相对独立的体系。前端的交互（如上传基因表达 CSV 文件）目前在后端还没有对接，目前是通过前端 `prediction_flow.js` 模拟。这就要求我们在 Python 后端构建真正的**基因数据通道**。

## 3. 集成改造方案 (Proposed Changes)

为了将高维度的 R 算法无缝接入当前的 Python 后端，我建议采用 **Subprocess 异步调用方案**，将具体的预测任务下发给 R 脚本执行。

### 3.1 核心对接逻辑设计

*   **新增 API 路由**：在 `app.py` 中新增类似 `/api/predict/gene` 的端点，专门用于接收用户上传的基因数据 CSV 文件。
*   **中间服务层 (R Wrapper)**：在 `backend` 中新建 `r_service.py`。该模块负责：
    1. 接收来自请求的 CSV 并在本地生成临时文件。
    2. 使用 `subprocess.run(["Rscript", ...])` 调用指定的 R 主脚本（如 `WGCNA干净数据/proposed.R`）。
    3. 获取 R 脚本抛出的 CSV 结果文件（如 `AUC` 或特征基因输出）。
    4. 将 R 的预测结果转换为 JSON 返回给前端呈现。
*   **R 脚本适配**：目前的 R 脚本多为十折交叉验证的“评估型”脚本。为了在线上用于真实病人的“预测”，我们需要提取原本 R 脚本中训练好最终模型的保存逻辑 (`saveRDS`) 和一个新的推理脚本 (`inference.R`) 专门用于读入单个样本进行预测。如果只需重跑现有交叉验证输出报告，则可以直接调用。

### 3.2 部署规划预研 (Deployment)

由于线上同时需要 Python (FastAPI/Flask) 和 R 环境，并且 R 环境依赖 `WGCNA` 和 GitHub 上特有的 `nielsrhansen/msgl` 包：
*   **Dockerfile 构建**：未来我们将采用多阶段构建的 Docker 镜像。底层基于 `ubuntu`，用 `apt` 安装 `r-base`，再安装 Python 环境。
*   **R 依赖清单**：需要编写 `install_packages.R` 用于在流水线中自动化安装所有库。

## 4. 后续执行步骤（待确认）

1.  **用户确认**：目前该方案重点是通过 Python 的 `subprocess` 调用 R 脚本并解析结果返回前端。R 环境需要由服务器本身支持。
2.  **代码执行**：确认后，我将在 `backend` 中添加一套 `r_integration_service.py`，并对 R 脚本中增加支持外部入参（如 `args <- commandArgs(trailingOnly=TRUE)`）的小型胶水文件，跑通第一次端到端测试。
