# setwd('../WGCNA')
data<-read.csv('cleandata.csv',header = T)
library(WGCNA) 
genedata=data[,179:198]##维数：
dim(genedata)
genedata<-t(genedata)#其中列是基因，行是样本
# Now we investigate soft thesholding with the power adjacency function 
powers1=c(seq(10,20,by=1),seq(21,33,by=2))  ##powers1: 1  2  3  4  5  6  7  8  9 10 12 14 16 18 20
RpowerTable1=pickSoftThreshold(genedata, powerVector=powers1)  ###
RpowerTable<-RpowerTable1[[2]]
gc() 
cex1=0.7 
# 横轴是Soft threshold (power)，纵轴是无标度网络的评估参数，数值越高，
# 网络越符合无标度特征 (non-scale)
par(mfrow=c(1,2)) 
plot(RpowerTable[,1], -sign(RpowerTable[,3])*RpowerTable[,2],xlab="
Soft Threshold (power)",ylab="Scale Free Topology Model Fit,R^2",type="n") 
text(RpowerTable[,1], -sign(RpowerTable[,3])*RpowerTable[,2], 
     labels=powers1,cex=cex1,col="red")   
# this line corresponds to using an R^2 cut-off of h 
abline(h=0.85,col="red") 
###
plot(RpowerTable[,1], RpowerTable[,5],xlab="Soft Threshold （power）",
     ylab="Mean Connectivity", type="n")
text(RpowerTable[,1], RpowerTable[,5], labels=powers1, cex=cex1,col="red")
net = blockwiseModules(genedata,
                       power = 29,                         # 软阀值选
                       TOMType = "unsigned",              # 构建无尺度网络
                       minModuleSize = 30,                # 最小模块基因数为30
                       mergeCutHeight = 0.1,             # 模块合并阀值
                       numericLabels = F,                 # 模块颜色标签
                       pamRespectsDendro = FALSE,         
                       saveTOMs = TRUE,                   # 保存TOM矩阵
                       verbose = 3,
                       maxBlockSize = 6000)               # 可以处理的数据集的最大基因数，默认5000
# 所有模块个数和各个模块中基因数量
table(net$colors)
datout2=data.frame(as.matrix(net$colors))
write.table(datout2, file="yanse-COID.csv", sep=",", row.names=F)
MEs = net$MEs # 模块特征向量
write.csv(MEs, file="mes-COID.csv", row.names=F)
datKME=signedKME(genedata, MEs, outputColumnName="kME_MM.")							
write.csv(datKME, "kME_MM-COID.csv")
geneTree = net$dendrograms[[1]] 
geneTree
#sizeGrWindow(12, 9)
#mergedColors = labels2colors(net$colors) 
plotDendroAndColors(net$dendrograms[[1]],
                    net$colors,
                    "Module colors",
                    dendroLabels = FALSE,
                    hang = 0.03,
                    addGuide = TRUE,
                    guideHang = 0.05)



