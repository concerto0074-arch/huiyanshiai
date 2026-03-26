rm(list =ls ())
# setwd('..')
MM<-read.csv('KME_MM-ADC.csv',header = T)
m1<-0
for (i in 1:1157) {
  tcolor<-MM[i,2]
  temp1<-1###
  if (tcolor==temp1){
    print(i)
    m1<-c(m1,i)
  }
}
m1<-MM[m1,3]###
#write.csv(m,'c1.csv')
m2<-0
for (i in 1:1157) {
  tcolor<-MM[i,2]
  temp1<-2###
  if (tcolor==temp1){
    print(i)
    m2<-c(m2,i)
  }
}
m2<-MM[m2,5]###
#write.csv(m,'c1.csv')
m3<-0
for (i in 1:1157) {
  tcolor<-MM[i,2]
  temp1<-3###
  if (tcolor==temp1){
    print(i)
    m3<-c(m3,i)
  }
}
m3<-MM[m3,4]###
#write.csv(m,'c1.csv')

MMADC<-c(m1,m2,m3)
write.csv(MMADC,'MMADC.csv')



