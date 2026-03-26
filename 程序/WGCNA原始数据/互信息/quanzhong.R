# setwd('.')
w1<-read.csv('wadc1.csv',header = F);w2<-read.csv('wadc2.csv',header = F)
w3<-read.csv('wadc3.csv',header = F);w4<-read.csv('wnl1.csv',header = F)
w5<-read.csv('wnl2.csv',header = F);w6<-read.csv('wnl3.csv',header = F)
w7<-read.csv('wnl4.csv',header = F)
w8<-read.csv('Wscc1.csv',header = F);w9<-read.csv('Wscc2.csv',header = F)
w10<-read.csv('Wscc3.csv',header = F);w11<-read.csv('Wscc4.csv',header = F)
w12<-read.csv('Wscc5.csv',header = F);w13<-read.csv('Wscc6.csv',header = F)
w14<-read.csv('Wscc7.csv',header = F);w15<-read.csv('Wscc8.csv',header = F)
w16<-read.csv('wcoid1.csv',header = F);w17<-read.csv('wcoid2.csv',header = F)
w18<-read.csv('wcoid3.csv',header = F);w19<-read.csv('wcoid4.csv',header = F)

w<-rbind(w1,w2,w3,w4,w5,w6,w7,w8,w9,w10,w11,w12,w13,w14,w15,w16,w17,w18,w19)
write.csv(w,'quanzhong.csv')
length(which(w[,3]==0))
