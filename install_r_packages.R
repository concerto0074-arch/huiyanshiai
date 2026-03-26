# R 依赖自动化安装脚本 (供 Docker 构建时使用)

# 设置 CRAN 镜像源以加速国内下载 (使用清华源)
options(repos = c(CRAN = "https://mirrors.tuna.tsinghua.edu.cn/CRAN/"))

# 核心系统依赖包
required_packages <- c(
  "devtools",
  "dqrng",
  "RcppArmadillo",
  "Matrix",
  "survival",
  "doParallel",
  "foreach"
)

# 自动安装 CRAN 系包
for(p in required_packages) {
  if (!require(p, character.only = TRUE)) {
    install.packages(p, dependencies = TRUE)
  }
}

# 安装 WGCNA 及其前置依赖 (Bioconductor 相关)
if (!require("BiocManager", quietly = TRUE)) {
  install.packages("BiocManager")
}
BiocManager::install(c("AnnotationDbi", "impute", "GO.db", "preprocessCore"))

if (!require("WGCNA", character.only = TRUE)) {
  install.packages("WGCNA")
}

# 安装特殊的 GitHub 系包 (msgl 用于核心算法)
library(devtools)
if (!require("msgl", character.only = TRUE)) {
  # nielsrhansen/msgl 是一个常用的 Multinomial Sparse Group Lasso 包
  install_github("nielsrhansen/msgl")
}

print("R 包安装检查完毕，准备就绪。")
