# 检查当前工作目录
current_wd <- getwd()
cat("当前工作目录：", current_wd, "\n")

# 检查WGCNA原始数据的完整路径
wgcna_path <- file.path("c:", "Users", "acer", "Desktop", "软件开发", "程序", "WGCNA原始数据")
cat("WGCNA原始数据路径：", wgcna_path, "\n")

# 验证路径是否存在
if (file.exists(wgcna_path)) {
  cat("路径存在！\n")
  # 列出该目录下的文件
  files <- list.files(wgcna_path)
  cat("目录下的文件：\n")
  head(files, 10)  # 只显示前10个文件
} else {
  cat("路径不存在！\n")
}