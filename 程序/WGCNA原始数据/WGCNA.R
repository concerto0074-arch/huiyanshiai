# setwd('.')
data<-read.csv('1157gene.csv',header = T)

# 安装BiocManager（若未安装）
if (!require("BiocManager", quietly = TRUE))
  install.packages("BiocManager")
# 安装WGCNA
BiocManager::install("WGCNA")
# 加载WGCNA包（修正拼写）

install.packages("DBI")
library(WGCNA)

 
genedata=data[,141:157]##ά����
dim(genedata)
genedata<-t(genedata)#�������ǻ�����������
# Now we investigate soft thesholding with the power adjacency function 
powers1=c(seq(1,10,by=1),seq(12,20,by=2))  ##powers1: 1  2  3  4  5  6  7  8  9 10 12 14 16 18 20
RpowerTable1=pickSoftThreshold(genedata, powerVector=powers1)  ###
RpowerTable<-RpowerTable1[[2]]
gc() 
cex1=0.7 
# ������Soft threshold (power)���������ޱ�������������������ֵԽ�ߣ�
# ����Խ�����ޱ������ (non-scale)
par(mfrow=c(1,2)) 
plot(RpowerTable[,1], -sign(RpowerTable[,3])*RpowerTable[,2],xlab="
Soft Threshold (power)",ylab="Scale Free Topology Model Fit,R^2",type="n") 
text(RpowerTable[,1], -sign(RpowerTable[,3])*RpowerTable[,2], 
     labels=powers1,cex=cex1,col="red")   
# this line corresponds to using an R^2 cut-off of h 
abline(h=0.85,col="red") 
###
plot(RpowerTable[,1], RpowerTable[,5],xlab="Soft Threshold ��power��",
     ylab="Mean Connectivity", type="n")
text(RpowerTable[,1], RpowerTable[,5], labels=powers1, cex=cex1,col="red")
net = blockwiseModules(genedata,
                       power = 12,                         # ����ֵѡ
                       TOMType = "unsigned",              # �����޳߶�����
                       minModuleSize = 30,                # ��Сģ�������Ϊ30
                       mergeCutHeight = 0.1,             # ģ��ϲ���ֵ
                       numericLabels = F,                 # ģ����ɫ��ǩ
                       pamRespectsDendro = FALSE,         
                       saveTOMs = TRUE,                   # ����TOM����
                       verbose = 3,
                       maxBlockSize = 6000)               # ���Դ��������ݼ�������������Ĭ��5000
# ����ģ������͸���ģ���л�������
table(net$colors)
datout2=data.frame(as.matrix(net$colors))
write.table(datout2, file="yanse-NL.csv", sep=",", row.names=F)
MEs = net$MEs # ģ����������
write.csv(MEs, file="mes-NL.csv", row.names=F)
datKME=signedKME(genedata, MEs, outputColumnName="kME_MM.")							
write.csv(datKME, "kME_MM-NL.csv")
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



