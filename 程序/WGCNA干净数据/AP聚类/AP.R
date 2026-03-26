# setwd('.')
data<-read.csv('cleandata.csv',header = T)
x<-data[,-1]
x<-as.matrix(x)
adc<-x[,1:139]
library(apcluster)
apres1 <- apcluster(negDistMat(r=20), adc, details=TRUE)
show(apres1)
index1<-c(1,apres1@clusters[[1]],2,apres1@clusters[[2]],3,apres1@clusters[[3]],
          4,apres1@clusters[[4]],5,apres1@clusters[[5]],6,apres1@clusters[[6]])
write.csv(index1,'indexadc.csv')

nl<-x[,140:156]
apres2 <- apcluster(negDistMat(r=5), nl, details=TRUE)
show(apres2)
index2<-c(1,apres2@clusters[[1]],2,apres2@clusters[[2]],3,apres2@clusters[[3]],
          4,apres2@clusters[[4]],5,apres2@clusters[[5]],6,apres2@clusters[[6]],
          7,apres2@clusters[[7]],8,apres2@clusters[[8]])
write.csv(index2,'indexnl.csv')

scc<-x[,157:177]
apres3 <- apcluster(negDistMat(r=50), scc, details=TRUE)
show(apres3)
index3<-c(1,apres3@clusters[[1]],2,apres3@clusters[[2]],3,apres3@clusters[[3]],
          4,apres3@clusters[[4]],5,apres3@clusters[[5]])
write.csv(index3,'indexscc.csv')

coid<-x[,178:197]
apres4 <- apcluster(negDistMat(r=20),coid, details=TRUE)
show(apres4)
index4<-c(1,apres4@clusters[[1]],2,apres4@clusters[[2]],3,apres4@clusters[[3]],
          4,apres4@clusters[[4]],5,apres4@clusters[[5]])
write.csv(index4,'indexcoid.csv')

