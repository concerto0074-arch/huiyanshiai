rm(list =ls ())
# setwd('..')
MM<-read.csv('KME_MM-SCC.csv',header = T)
m1<-0
for (i in 1:1157) {
  tcolor<-MM[i,2]
  temp1<-1###
  if (tcolor==temp1){
    print(i)
    m1<-c(m1,i)
  }
}
m1<-MM[m1,8]###
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
m2<-MM[m2,6]###
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
m3<-MM[m3,7]###
#write.csv(m,'c1.csv')
m4<-0
for (i in 1:1157) {
  tcolor<-MM[i,2]
  temp1<-4###
  if (tcolor==temp1){
    print(i)
    m4<-c(m4,i)
  }
}
m4<-MM[m4,3]###
#write.csv(m,'c1.csv')
m5<-0
for (i in 1:1157) {
  tcolor<-MM[i,2]
  temp1<-5###
  if (tcolor==temp1){
    print(i)
    m5<-c(m5,i)
  }
}
m5<-MM[m5,10]###
#write.csv(m,'c1.csv')
m6<-0
for (i in 1:1157) {
  tcolor<-MM[i,2]
  temp1<-6###
  if (tcolor==temp1){
    print(i)
    m6<-c(m6,i)
  }
}
m6<-MM[m6,5]###
#write.csv(m,'c1.csv')
m7<-0
for (i in 1:1157) {
  tcolor<-MM[i,2]
  temp1<-7###
  if (tcolor==temp1){
    print(i)
    m7<-c(m7,i)
  }
}
m7<-MM[m7,9]###
#write.csv(m,'c1.csv')
m8<-0
for (i in 1:1157) {
  tcolor<-MM[i,2]
  temp1<-8###
  if (tcolor==temp1){
    print(i)
    m8<-c(m8,i)
  }
}
m8<-MM[m8,4]###
#write.csv(m,'c1.csv')

MMSCC<-c(m1,m2,m3,m4,m5,m6,m7,m8)
write.csv(MMSCC,'MMSCC.csv')



