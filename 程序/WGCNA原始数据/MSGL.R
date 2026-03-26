# setwd('../不重叠分群')
gene<-read.csv('1157gene.csv')
index<-gene[,2]
x<-gene[,-c(1:2)]
x<-t(x)
x<-as.matrix(x)# (行样本列基因)
dim(x)
ytrain=c(rep(1,93),rep(2,11),rep(3,14),rep(4,13))
ytrain<-as.factor(ytrain)
table(ytrain)
ytest=c(rep(1,46),rep(2,6),rep(3,7),rep(4,7))
ytest<-as.factor(ytest)## 将leibioaoqian赋给y,属性改为因子
#种子
ar<-c();hr<-c();TP1<-c();TP2<-c();TP3<-c();TP4<-c()
FN1<-c();FN2<-c();FN3<-c();FN4<-c()
FP1<-c();FP2<-c();FP3<-c();FP4<-c()
TN1<-c();TN2<-c();TN3<-c();TN4<-c()
P1<-c();P2<-c();P3<-c();P4<-c()
R1<-c();R2<-c();R3<-c();R4<-c()
AUC<-matrix(nrow=66,ncol=10)
for (i in 1:10){
  set.seed(i)
  #2/3训练
  lungAD=x[1:139,]##维数：
  dim(lungAD)
  index1<-sample(1:nrow(lungAD),round(2/3*(nrow(lungAD))))
  lungADtrain<-lungAD[index1,]
  lungADtest<-lungAD[-index1,]
  
  lungNL=x[140:156,]##维数：
  dim(lungNL)
  index4<-sample(1:nrow(lungNL),round(2/3*(nrow(lungNL))))
  lungNLtrain<-lungNL[index4,]
  lungNLtest<-lungNL[-index4,]
  
  lungSQ=x[157:177,]##维数：
  dim(lungSQ)
  index2<-sample(1:nrow(lungSQ),round(2/3*(nrow(lungSQ))))
  lungSQtrain<-lungSQ[index2,]
  lungSQtest<-lungSQ[-index2,]
  
  lungCOID=x[178:197,]##维数：
  dim(lungCOID)
  index3<-sample(1:nrow(lungCOID),round(2/3*(nrow(lungCOID))))
  lungCOIDtrain<-lungCOID[index3,]
  lungCOIDtest<-lungCOID[-index3,]
  
  #3 #合并
  xtrain<-rbind(lungADtrain, lungNLtrain, lungSQtrain,lungCOIDtrain)
  dim(xtrain)
  xtest<-rbind(lungADtest, lungNLtest, lungSQtest,lungCOIDtest)
  dim(xtest)
  
  library(msgl)
  #####################采用十折交叉验证##############################
  # Using a lambda sequence ranging from the maximal lambda to 0.7 * maximal lambda
  cl <- makeCluster(4)
  registerDoParallel(cl)
  fit.cv <- msgl::cv(xtrain, classes=ytrain,grouping=index,
                     alpha=0.5, 
                     lambda = 0.05, use_parallel = TRUE)
  stopCluster(cl)
  ################拟合最终模型###################################
  fit <- msgl::fit(xtrain,classes=ytrain, grouping=index,
                   alpha = 0.5,
                   lambda = 0.05)
  n<-features(fit)[[best_model(fit.cv)]] # 最优模型中的非零特征
  hr[i]<-length(n)
  #n
  
  ################### 预  测 #########################################
  res <- predict(fit,xtest)
  yyuce<-res$classes[,best_model(fit.cv)] # Classes predicted by best model
  AUC[,i]<-yyuce
  as.numeric(yyuce)
  as.numeric(ytest)
  as.numeric(ytest)-as.numeric(yyuce)
  #hunxiaojuzhen
  cft<-table(yyuce,ytest)
  TP1[i]<-cft[1,1];FN1[i]<-cft[1,2]+cft[1,3]+cft[1,4]
  FP1[i]<-cft[2,1]+cft[3,1]+cft[4,1];TN1[i]<-66-(TP1[i]+FN1[i]+FP1[i])
  TP2[i]<-cft[2,2];FN2[i]<-cft[2,1]+cft[2,3]+cft[2,4]
  FP2[i]<-cft[1,2]+cft[3,2]+cft[4,2];TN2[i]<-66-(TP2[i]+FN2[i]+FP2[i])
  TP3[i]<-cft[3,3];FN3[i]<-cft[3,1]+cft[3,2]+cft[3,4]
  FP3[i]<-cft[1,3]+cft[2,3]+cft[4,3];TN3[i]<-66-(TP3[i]+FN3[i]+FP3[i])
  TP4[i]<-cft[4,4];FN4[i]<-cft[4,1]+cft[4,3]+cft[4,2]
  FP4[i]<-cft[1,4]+cft[3,4]+cft[2,4];TN4[i]<-66-(TP4[i]+FN4[i]+FP4[i])
  P1[i]<-TP1[i]/(TP1[i]+FP1[i]);R1[i]<-TP1[i]/(TP1[i]+FN1[i])
  P2[i]<-TP2[i]/(TP2[i]+FP2[i]);R2[i]<-TP2[i]/(TP2[i]+FN2[i])
  P3[i]<-TP3[i]/(TP3[i]+FP3[i]);R3[i]<-TP3[i]/(TP3[i]+FN3[i])
  P4[i]<-TP4[i]/(TP4[i]+FP4[i]);R4[i]<-TP4[i]/(TP4[i]+FN4[i])
  #
  acc<-length(which(as.numeric(ytest)-as.numeric(yyuce)==0))/66
  ar[i]<-acc
}
TP1;FN1;FP1;TN1;P1;R1;TP2;FN2;FP2;TN2;P2;R2
TP3;FN3;FP3;TN3;P3;R3;TP4;FN4;FP4;TN4;P4;R4
mean(TP1);mean(FN1);mean(FP1);mean(TN1);mean(P1);mean(R1);mean(TP2);mean(FN2);mean(FP2);mean(TN2);mean(P2);mean(R2)
mean(TP3);mean(FN3);mean(FP3);mean(TN3);mean(P3);mean(R3);mean(TP4);mean(FN4);mean(FP4);mean(TN4);mean(P4);mean(R4)
ar
hr
mean(ar)
sd(ar)
mean(hr)
sd(hr)
write.csv(AUC,'AUC-MSGL-noise.csv')


