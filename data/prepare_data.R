# 下载并准备乳腺癌数据集
# 加载必要的包
install.packages("mlbench", dependencies = TRUE)
library(mlbench)

# 加载乳腺癌数据集
data(BreastCancer)

# 查看数据集结构
print(str(BreastCancer))

# 移除ID列（不需要用于预测）
BreastCancer <- BreastCancer[, -1]

# 移除包含缺失值的行
BreastCancer <- na.omit(BreastCancer)

# 将分类变量转换为数值型
BreastCancer$Class <- ifelse(BreastCancer$Class == "malignant", 1, 0)
for (col in 2:9) {
  BreastCancer[[col]] <- as.numeric(as.character(BreastCancer[[col]]))
}

# 查看处理后的数据结构
print(str(BreastCancer))

# 保存数据集为CSV文件
write.csv(BreastCancer, file = "data/breast_cancer.csv", row.names = FALSE)

print("数据集准备完成！")