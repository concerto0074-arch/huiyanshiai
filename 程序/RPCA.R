###��ȡ����
# 获取脚本所在目录
args <- commandArgs(trailingOnly = FALSE)
script_path <- args[grep("^--file=", args)]
script_path <- sub("^--file=", "", script_path)
script_dir <- dirname(script_path)
# 构建输入文件的完整路径
input_file <- file.path(script_dir, '1157gene.csv')
lungdata<-read.csv(input_file)
dim(lungdata)
lungdata1<-as.matrix(t(lungdata[,-1]))
dim(lungdata1)
geneid<-as.matrix(lungdata[,1])

###����RPCA,��������Candes����Ĭ��ֵ
library(rpca)

res<-rpca(lungdata1, lambda = 1/sqrt(max(dim(lungdata1))), mu = prod(dim(lungdata1))/(4*sum(abs(lungdata1))),
          term.delta = 10^(-7), max.iter = 10000, trace = FALSE,
          thresh.nuclear.fun = thresh.nuclear, thresh.l1.fun = thresh.l1,
          F2norm.fun = F2norm)

###��ȡ���������
lunglow<-res$L
dim(lunglow)
#���ϻ���
lunglow<-t(lunglow)
lunglow<-cbind(geneid,lunglow)
lungnoise<-res$S
lungnoise<-t(lungnoise)
lungnoise<-cbind(geneid,lungnoise)
# 构建输出文件的完整路径
output_clean <- file.path(script_dir, 'cleandata.csv')
output_noise <- file.path(script_dir, 'noisedata.csv')
write.table(lunglow, file=output_clean, sep=",", row.names=F) 
write.table(lungnoise, file=output_noise, sep=",", row.names=F) 
