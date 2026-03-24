# 使用Python下载并准备乳腺癌数据集
# 加载必要的库
import pandas as pd
from sklearn.datasets import load_breast_cancer

# 加载乳腺癌数据集
cancer = load_breast_cancer()

# 创建DataFrame
X = pd.DataFrame(cancer.data, columns=cancer.feature_names)
y = pd.DataFrame(cancer.target, columns=['Class'])

# 合并特征和标签
breast_cancer_df = pd.concat([X, y], axis=1)

# 将标签转换：0=良性，1=恶性（与原数据集相反，保持一致性）
breast_cancer_df['Class'] = breast_cancer_df['Class'].apply(lambda x: 1 if x == 0 else 0)

# 查看数据集结构
print("数据集形状:", breast_cancer_df.shape)
print("数据集列名:", list(breast_cancer_df.columns))
print("前5行数据:")
print(breast_cancer_df.head())

# 保存数据集为CSV文件
breast_cancer_df.to_csv('data/breast_cancer.csv', index=False)

print("\n数据集准备完成！")