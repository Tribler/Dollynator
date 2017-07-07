library(readr)
plebmail_log <- read_csv("~/BEP/DATA/final_plebmail.log.csv")


MB = 1024 * 1024
GB = MB * 1024

log_lists <- split(plebmail_log, plebmail_log$ip)


servers <- list()
maxx <- 0
maxy <- 0
i <- 0
for(server in log_lists){
  first_time = min(server$time)
  first_recv = min(server$recv)
  first_sent = min(server$sent)
  
  server$time <- server$time - first_time
  server$recv <- server$recv - first_recv
  server$sent <- server$sent - first_sent
  
  server$MC_potential <- pmin(server$recv, server$sent) / GB / 5
  server$recv <- server$recv / GB
  server$sent <- server$sent / GB
  server$ram <- server$ram / GB
  server$ram_ava <- server$ram_ava / GB
  server$time <- server$time / 60 /60 /24
  
  mx <- max(server$time)
  my <- max(server$MC_potential)
  if(mx > maxx){
    maxx <- mx
  }
  if(my > maxy){
    maxy <- my
  }

}
i=0
for(server in log_lists){
  first_time = min(server$time)
  first_recv = min(server$recv)
  first_sent = min(server$sent)
  
  server$time <- server$time - first_time
  server$recv <- server$recv - first_recv
  server$sent <- server$sent - first_sent
  
  server$MC_potential <- pmin(server$recv, server$sent) / GB / 5
  server$recv <- server$recv / GB
  server$sent <- server$sent / GB
  server$ram <- server$ram / GB
  server$ram_ava <- server$ram_ava / GB
  server$time <- server$time / 60 / 60 / 24

  serverx <- server
  if(i==0){
    plot(serverx$time, serverx$MC_potential,xlim=c(0,maxx),ylim=c(0,maxy), type='l', xlab='Days', ylab='Number of HD Movies')
  }
  else{
    lines(serverx$time, serverx$MC_potential,type='l', xlab='', ylab='')
  }
  
  i <- i + 1
}

