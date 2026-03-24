import pandas as pd
import numpy as np

# 生成模拟的癌症数据
np.random.seed(42)

# 样本数量
n_samples = 1000

# 特征：年龄、性别、BMI、吸烟史、肿瘤标志物1、肿瘤标志物2、基因突变
age = np.random.randint(20, 80, n_samples)
gender = np.random.randint(0, 2, n_samples)  # 0=男, 1=女
bmi = np.round(np.random.uniform(18, 35, n_samples), 1)
smoking = np.random.randint(0, 3, n_samples)  # 0=从不, 1=曾经, 2=现在
tumor_marker1 = np.round(np.random.uniform(0, 200, n_samples), 1)
tumor_marker2 = np.round(np.random.uniform(0, 100, n_samples), 1)
mutation = np.random.randint(0, 2, n_samples)  # 0=无, 1=有

# 标签：癌症风险（0=低, 1=中, 2=高）
# 基于特征生成风险标签
risk = np.zeros(n_samples)
risk[(age > 50) & (smoking == 2) & (tumor_marker1 > 100)] = 2  # 高风险
temp_mask = (age > 40) & (smoking >= 1) & (tumor_marker1 > 50) & (risk == 0)
risk[temp_mask] = 1  # 中风险

# 创建DataFrame
df = pd.DataFrame({
    'age': age,
    'gender': gender,
    'bmi': bmi,
    'smoking': smoking,
    'tumor_marker1': tumor_marker1,
    'tumor_marker2': tumor_marker2,
    'mutation': mutation,
    'risk': risk.astype(int)
})

# 保存数据
df.to_csv('data/cancer_data.csv', index=False)
print(f"生成数据完成，共{len(df)}条样本")
print("数据分布：")
print(df['risk'].value_counts())
