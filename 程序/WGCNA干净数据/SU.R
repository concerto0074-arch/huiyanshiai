rm(list = ls())
# setwd('.')
####计算group weight
library(FCBF)
mesAD<-read.csv('mes-ADC.csv')
mesSQ<-read.csv('mes-SCC.csv')
mesCOID<-read.csv('mes-COID.csv')
mesNL<-read.csv('mes-NL.csv')

colnames(mesAD)<-mesAD[1,]
mesAD<-mesAD[-1,]
colnames(mesSQ)<-mesSQ[1,]
mesSQ<-mesSQ[-1,]
colnames(mesCOID)<-mesCOID[1,]
mesCOID<-mesCOID[-1,]
colnames(mesNL)<-mesNL[1,]
mesNL<-mesNL[-1,]

library(Matrix)
dd<-bdiag(as.matrix(mesAD),as.matrix(mesNL),as.matrix(mesSQ),as.matrix(mesCOID))
mes<-abs(t(as.matrix(dd)))
y<-c(rep(1,139),rep(2,17),rep(3,21),rep(4,20))
discrete_expression <- as.data.frame(discretize_exprs(mes))#离散化
su<- get_su_for_feature_table_and_vector(discrete_expression[,],y)
#write.csv(su,'su.csv')
a<-read.csv("a.csv",header = F)
for (i in 1:24) {
  temp1<-a[i,1]
  for (j in 1:24) {
    temp2<-su[j,2]
    if (temp1==temp2){
      a[i,2]<-su[j,1]
    }
  }
}
write.csv(a,'paixusu.csv')



