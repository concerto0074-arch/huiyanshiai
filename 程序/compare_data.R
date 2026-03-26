# setwd('.')
original <- read.csv('1157gene.csv', row.names = 1)
clean <- read.csv('cleandata.csv', row.names = 1)
noise <- read.csv('noisedata.csv', row.names = 1)

# 检查维度是否一致
cat('Original dimensions:', dim(original), '\n')
cat('Clean dimensions:', dim(clean), '\n')
cat('Noise dimensions:', dim(noise), '\n')

# 检查 clean + noise 是否等于原始数据
# 由于浮点运算误差，我们需要使用近似比较
diff <- original - (clean + noise)
max_diff <- max(abs(diff))
cat('Maximum difference between original and (clean + noise):', max_diff, '\n')

# 检查有多少值的差异大于1e-6（一个小的阈值）
significant_diff <- sum(abs(diff) > 1e-6)
cat('Number of values with difference > 1e-6:', significant_diff, '\n')

# 显示一些示例值
cat('\nSample values:\n')
cat('Original[1,1]:', original[1,1], '\n')
cat('Clean[1,1]:', clean[1,1], '\n')
cat('Noise[1,1]:', noise[1,1], '\n')
cat('Clean[1,1] + Noise[1,1]:', clean[1,1] + noise[1,1], '\n')
cat('Difference:', original[1,1] - (clean[1,1] + noise[1,1]), '\n')

# 统计clean和noise数据的一些基本特性
# 将data.frame转换为矩阵进行统计计算
clean_mat <- as.matrix(clean)
noise_mat <- as.matrix(noise)

cat('\nClean data statistics:\n')
cat('Mean:', mean(clean_mat), '\n')
cat('Standard deviation:', sd(clean_mat), '\n')
cat('Min:', min(clean_mat), '\n')
cat('Max:', max(clean_mat), '\n')

cat('\nNoise data statistics:\n')
cat('Mean:', mean(noise_mat), '\n')
cat('Standard deviation:', sd(noise_mat), '\n')
cat('Min:', min(noise_mat), '\n')
cat('Max:', max(noise_mat), '\n')

# 计算非零噪声值的比例
non_zero_noise <- sum(noise != 0) / (nrow(noise) * ncol(noise)) * 100
cat('\nPercentage of non-zero noise values:', round(non_zero_noise, 2), '%\n')
